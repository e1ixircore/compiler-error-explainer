import ast
import re

# Dotted-name blocklist. Resolving the full name (os.system, not just .system)
# means we catch subprocess.run etc. without flagging every method named run().
DANGEROUS = {
    "os.system": ("Command Injection", "CRITICAL"),
    "os.popen": ("Command Injection", "CRITICAL"),
    "subprocess.run": ("Command Injection", "CRITICAL"),
    "subprocess.Popen": ("Command Injection", "CRITICAL"),
    "subprocess.call": ("Command Injection", "CRITICAL"),
    "subprocess.check_output": ("Command Injection", "CRITICAL"),
    "eval": ("Arbitrary Code Execution", "HIGH"),
    "exec": ("Arbitrary Code Execution", "HIGH"),
    "__import__": ("Arbitrary Code Execution", "HIGH"),
    "shutil.rmtree": ("Destructive File Operation", "HIGH"),
    # NEW: single-file deletion (test_sec_del.py promises os.remove is HIGH)
    "os.remove": ("Destructive File Operation", "HIGH"),
    "os.unlink": ("Destructive File Operation", "HIGH"),
    "os.rmdir": ("Destructive File Operation", "HIGH"),
}

# NEW: modules whose mere import is a finding (root package name -> (type, severity, why)).
RISKY_IMPORTS = {
    "ctypes": ("Native Code Access", "HIGH", "ctypes can bypass Python's safety checks."),
    "socket": ("Network Access", "MEDIUM", "socket gives the program network access."),
}

# NEW: attributes that only appear in well-known sandbox-escape tricks,
# e.g. ().__class__.__bases__[0].__subclasses__()
ESCAPE_ATTRS = {"__subclasses__", "__globals__", "__builtins__", "__mro__"}

# NEW: getattr(os, 'system') hides a dangerous name inside a string. We look at the string.
DANGEROUS_ATTR_NAMES = {k.split(".")[-1] for k in DANGEROUS} | {"run", "call"}


def _dotted(node):
    """ast.Attribute chain -> 'os.path.join'; None if the base isn't a plain name."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        return f"{base}.{node.attr}" if base else None
    return None


def _alias_map(tree):
    """NEW: nickname -> real dotted name, built from the file's own imports.
        import os as o              ->  {'o': 'os'}
        from subprocess import run as r  ->  {'r': 'subprocess.run'}
        from os import system       ->  {'system': 'os.system'}
    Without this, o.system(...) is looked up as 'o.system' and slips past the blocklist."""
    amap = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.asname:
                    amap[a.asname] = a.name
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            for a in n.names:
                amap[a.asname or a.name] = f"{n.module}.{a.name}"
    return amap


def _resolve(node, amap):
    """Dotted name of a call target with import nicknames replaced by the real module."""
    name = _dotted(node)
    if not name:
        return None
    head, _, rest = name.partition(".")
    if head in amap:
        name = amap[head] + ("." + rest if rest else "")
    return name[len("builtins."):] if name.startswith("builtins.") else name


def _opens_for_write(call):
    """NEW: open(path, 'w'/'a'/'x'/'+') with a literal mode (positional or mode=)."""
    mode = call.args[1] if len(call.args) > 1 else next(
        (k.value for k in call.keywords if k.arg == "mode"), None)
    return (isinstance(mode, ast.Constant) and isinstance(mode.value, str)
            and any(c in mode.value for c in "wax+"))


# C++ security rules (regex-based on comment/string-stripped source).
_CPP_DANGEROUS_CALLS = [
    (re.compile(r"\b(?:std::)?system\s*\("), "Command Injection", "CRITICAL", "system() executes arbitrary shell commands."),
    (re.compile(r"\b(?:_)?popen\s*\("), "Command Injection", "CRITICAL", "popen() executes arbitrary shell commands."),
    (re.compile(r"\bexec(?:l|le|lp|v|vp|ve|vpe)\s*\("), "Command Injection", "CRITICAL", "exec*() spawns external processes."),
    (re.compile(r"\bShellExecute[AW]?\s*\("), "Command Injection", "CRITICAL", "ShellExecute() launches external commands."),
    (re.compile(r"\b(?:v)?fork\s*\("), "Process Manipulation", "HIGH", "fork() creates new OS processes."),
    (re.compile(r"\b(?:__)?asm(?:__)?\s*[\(\{]"), "Inline Assembly", "HIGH", "Inline assembly bypasses compiler safety checks."),
    (re.compile(r"\b(?:std::filesystem::remove_all|std::filesystem::remove)\s*\("), "Destructive File Operation", "HIGH", "filesystem remove deletes files or directories."),
    (re.compile(r"\b(?:std::)?remove\s*\("), "Destructive File Operation", "HIGH", "remove() deletes files from disk."),
    (re.compile(r"\b(?:unlink|rmdir)\s*\("), "Destructive File Operation", "HIGH", "unlink()/rmdir() deletes files or directories."),
    (re.compile(r"\bgets\s*\("), "Buffer Overflow", "HIGH", "gets() is unsafe and removed from modern C++ (use std::getline)."),
    (re.compile(r"\b(?:strcpy|strcat|sprintf)\s*\("), "Unsafe Memory Function", "MEDIUM", "Unbounded C string function can cause buffer overflow (prefer std::string or snprintf)."),
    (re.compile(r"\b(?:std::)?ofstream\b"), "File Write", "MEDIUM", "std::ofstream writes to files on disk."),
    (re.compile(r"\bfopen\s*\([^,\n]+,\s*\x00"), "File Write", "MEDIUM", "fopen() accesses files on disk."),
]

_CPP_RISKY_HEADERS = {
    "sys/socket.h": ("Network Access", "MEDIUM", "sys/socket.h gives the program raw network socket access."),
    "netinet/in.h": ("Network Access", "MEDIUM", "netinet/in.h gives the program network access."),
    "winsock2.h": ("Network Access", "MEDIUM", "winsock2.h gives the program network access."),
}


def _strip_cpp_comments_and_strings(code):
    """Replace C++ comments and string/char literal bodies with spaces/\\x00, preserving newlines."""
    out, i, n = [], 0, len(code)
    while i < n:
        c = code[i]
        if c == "/" and i + 1 < n and code[i + 1] == "/":
            j = code.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
            continue
        if c == "/" and i + 1 < n and code[i + 1] == "*":
            j = code.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join("\n" if ch == "\n" else " " for ch in code[i:j]))
            i = j
            continue
        if c in ('"', "'"):
            q = c
            out.append("\x00")
            i += 1
            while i < n:
                if code[i] == "\\" and i + 1 < n:
                    out.append("\n" if code[i + 1] == "\n" else "\x00")
                    i += 2
                    continue
                if code[i] == q:
                    out.append("\x00")
                    i += 1
                    break
                out.append("\n" if code[i] == "\n" else "\x00")
                i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


class SecurityAnalyzer:
    def __init__(self):
        """
        Security Enforcement Mechanism (AST based blocklist for Python, lexical blocklist for C++).
        Detects: command injection, arbitrary code execution, destructive file operations,
        insecure temp files, hardcoded secrets, plus (new) import-alias evasion,
        getattr-by-name, ctypes, sandbox-escape attributes, network imports, file writes.
        It is still a BLOCKLIST: it cannot catch everything (see README).
        """
        pass

    def scan_cpp_code(self, code_string):
        """Scan C++ source for dangerous calls, risky headers, and hardcoded secrets."""
        vulnerabilities = []
        raw_lines = code_string.split("\n")
        cleaned_lines = _strip_cpp_comments_and_strings(code_string).split("\n")

        for lineno, (raw, clean) in enumerate(zip(raw_lines, cleaned_lines), 1):
            inc = re.match(r"^\s*#\s*include\s*[<\"]([^>\"]+)[>\"]", raw)
            if inc:
                hdr = inc.group(1).strip()
                if hdr in _CPP_RISKY_HEADERS:
                    vtype, sev, msg = _CPP_RISKY_HEADERS[hdr]
                    vulnerabilities.append({"type": vtype, "severity": sev, "message": f"#include <{hdr}>: {msg}", "line": lineno})
                continue

            for pat, vtype, sev, msg in _CPP_DANGEROUS_CALLS:
                # Special check for fopen: only flag write/append modes.
                if pat.pattern.startswith(r"\bfopen"):
                    if re.search(r'\bfopen\s*\([^,\n]+,\s*"[^"]*[wa+]', raw):
                        vulnerabilities.append({"type": vtype, "severity": sev, "message": msg, "line": lineno})
                elif pat.search(clean):
                    vulnerabilities.append({"type": vtype, "severity": sev, "message": msg, "line": lineno})

            sec_m = re.search(r"\b([A-Za-z_]\w*(?:password|secret|api_key|token)\w*)\s*=\s*\"[^\"]+\"", raw, re.IGNORECASE)
            if sec_m:
                vulnerabilities.append({
                    "type": "Hardcoded Secret",
                    "severity": "LOW",
                    "message": f"Potential hardcoded secret detected in variable '{sec_m.group(1)}'.",
                    "line": lineno,
                })
        return vulnerabilities

    def scan_code(self, code_string, language="python"):
        """
        Parses the code string and returns a list of detected vulnerabilities.
        """
        if language == "cpp":
            return self.scan_cpp_code(code_string)
        vulnerabilities = []
        try:
            tree = ast.parse(code_string)
        except SyntaxError:
            return vulnerabilities          # let the sandbox report it with a line number
        except (RecursionError, MemoryError, ValueError):
            # Hostile/pathological input: refuse it instead of crashing the compiler.
            return [{"type": "Unanalyzable Input", "severity": "HIGH",
                     "message": "Input too deeply nested or malformed to analyze safely.",
                     "line": 1}]

        def add(node, vtype, sev, msg):
            vulnerabilities.append({"type": vtype, "severity": sev, "message": msg,
                                    "line": getattr(node, "lineno", "Unknown")})

        amap = _alias_map(tree)

        for node in ast.walk(tree):

            # Insecure Temporary Files
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == 'mktemp':
                    add(node, "Insecure Temp File", "MEDIUM",
                        "mktemp() is insecure. Use tempfile.mkstemp() instead.")

            # Hardcoded Secrets
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        if any(secret in var_name for secret in ['password', 'secret', 'api_key', 'token']):
                            vulnerabilities.append({
                                "type": "Hardcoded Secret",
                                "severity": "LOW",
                                "message": f"Potential hardcoded secret detected in variable '{target.id}'.",
                                "line": getattr(target, 'lineno', 'Unknown')
                            })

            if isinstance(node, ast.Call):
                # Calls: dotted name AFTER alias resolution (catches o.system, r(...), system(...))
                name = _resolve(node.func, amap)
                if name in DANGEROUS:
                    t, sev = DANGEROUS[name]
                    add(node, t, sev, f"{name}() detected.")
                # NEW: getattr(os, 'system') / getattr(x, '__subclasses__')
                elif name == "getattr" and len(node.args) >= 2:
                    k = node.args[1]
                    if isinstance(k, ast.Constant) and isinstance(k.value, str) and \
                            (k.value in DANGEROUS_ATTR_NAMES or k.value in ESCAPE_ATTRS):
                        add(node, "Dynamic Attribute Access", "HIGH",
                            f"getattr(..., '{k.value}') fetches a dangerous name indirectly.")
                # NEW: open(path, 'w')
                elif name == "open" and _opens_for_write(node):
                    add(node, "File Write", "MEDIUM", "open() in a write/append mode modifies files.")

            # NEW: ().__class__.__bases__[0].__subclasses__() style escapes
            if isinstance(node, ast.Attribute) and node.attr in ESCAPE_ATTRS:
                add(node, "Sandbox Escape", "HIGH", f"Access to {node.attr} is a known sandbox-escape trick.")

            # NEW: risky imports (ctypes, socket) in both import forms
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] if isinstance(node, ast.Import) \
                    else [node.module or ""]
                for m in mods:
                    root = m.split(".")[0]
                    if root in RISKY_IMPORTS:
                        t, sev, why = RISKY_IMPORTS[root]
                        add(node, t, sev, f"import {m}: {why}")

            # `from os import system` hides the module from the call site.
            # Generalised: any 'module.name' that is on the blocklist (os, subprocess, shutil...).
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                for a in node.names:
                    key = f"{node.module}.{a.name}"
                    if key in DANGEROUS:
                        t, sev = DANGEROUS[key]
                        add(node, t, sev, f"from {node.module} import {a.name} bypasses call-site checks.")

        return vulnerabilities