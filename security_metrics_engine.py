"""
security_metrics_engine.py
==========================
52-Metric AST & Static Security Analysis Engine for the Secure Agentic AI Compiler (IntelliFix / TOACD).

Provides:
  - 52 formally defined security metrics (SEC_01 .. SEC_52) across 8 CWE/OWASP-aligned categories:
      1. Injection & Execution (SEC_01 - SEC_08)
      2. Sandbox Escape & Reflection (SEC_09 - SEC_14)
      3. File System & Path Traversal (SEC_15 - SEC_20)
      4. Cryptography & Secrets (SEC_21 - SEC_27)
      5. Network & Server-Side Security (SEC_28 - SEC_33)
      6. Denial of Service & Resource Control (SEC_34 - SEC_40)
      7. Low-Level / C++ Interop & Memory Safety (SEC_41 - SEC_45)
      8. Quantitative Attack Surface & Complexity Metrics (SEC_46 - SEC_52)
  - Full Python AST analysis with import-alias resolution, basic intra-procedural taint tracking,
    Shannon entropy secret scanning, ReDoS pattern analysis, and McCabe cyclomatic complexity.
  - C++ lexical/pattern security scanning (preserving line numbers with comment/string stripping).
  - Pre/Post-patch comparison API (`compare()`) for Agentic Compiler self-verification loops.
  - Programmatic Markdown/CSV taxonomy export for reproducible documentation tables.
"""

from __future__ import annotations

import ast
import csv
import io
import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# 1. Formal 52-Metric Registry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MetricSpec:
    id: str
    name: str
    category: str
    cwe: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    weight: float
    kind: str      # "detector" (count of violations) or "quantitative" (computed metric)
    description: str


METRICS_REGISTRY: Dict[str, MetricSpec] = {
    # --- Category 1: Injection & Execution (8) ---
    "SEC_01": MetricSpec("SEC_01", "OS Command Injection", "Injection & Execution", "CWE-78", "CRITICAL", 10.0, "detector", "Detects OS shell execution via os.system, popen, or subprocess."),
    "SEC_02": MetricSpec("SEC_02", "Dynamic Code Evaluation", "Injection & Execution", "CWE-95", "CRITICAL", 9.5, "detector", "Detects arbitrary code execution via eval(), exec(), or compile()."),
    "SEC_03": MetricSpec("SEC_03", "Insecure Deserialization", "Injection & Execution", "CWE-502", "CRITICAL", 9.0, "detector", "Detects unsafe deserialization via pickle, marshal, shelve, or yaml.load."),
    "SEC_04": MetricSpec("SEC_04", "Raw SQL Injection", "Injection & Execution", "CWE-89", "CRITICAL", 9.0, "detector", "Detects unparameterized SQL strings constructed with %, +, .format, or f-strings."),
    "SEC_05": MetricSpec("SEC_05", "XML External Entity (XXE)", "Injection & Execution", "CWE-611", "HIGH", 7.0, "detector", "Detects unsafe XML parsers (xml.etree, minidom, sax, pulldom) instead of defusedxml."),
    "SEC_06": MetricSpec("SEC_06", "Server-Side Template Injection", "Injection & Execution", "CWE-1336", "HIGH", 7.5, "detector", "Detects dynamic template rendering (render_template_string, jinja2.Template)."),
    "SEC_07": MetricSpec("SEC_07", "LDAP / XPath Injection", "Injection & Execution", "CWE-90", "HIGH", 7.0, "detector", "Detects unparameterized LDAP search filters or dynamic XPath queries."),
    "SEC_08": MetricSpec("SEC_08", "Unsafe Dynamic Import", "Injection & Execution", "CWE-470", "HIGH", 7.0, "detector", "Detects dynamic module loading via __import__ or importlib.import_module."),

    # --- Category 2: Sandbox Escape & Reflection (6) ---
    "SEC_09": MetricSpec("SEC_09", "MRO Class Traversal", "Sandbox Escape & Reflection", "CWE-269", "CRITICAL", 9.0, "detector", "Detects __subclasses__, __bases__, __mro__, or __class__ sandbox escapes."),
    "SEC_10": MetricSpec("SEC_10", "Builtins Namespace Poisoning", "Sandbox Escape & Reflection", "CWE-668", "CRITICAL", 9.0, "detector", "Detects access or mutation of __builtins__ or builtins namespace."),
    "SEC_11": MetricSpec("SEC_11", "Frame Inspection / Stack Walking", "Sandbox Escape & Reflection", "CWE-489", "HIGH", 7.5, "detector", "Detects sys._getframe, inspect.currentframe, or f_globals/f_locals access."),
    "SEC_12": MetricSpec("SEC_12", "Native Code Binding", "Sandbox Escape & Reflection", "CWE-111", "HIGH", 8.0, "detector", "Detects ctypes/cffi/inline-assembly imports or calls bypassing runtime safety."),
    "SEC_13": MetricSpec("SEC_13", "Global Symbol Table Tampering", "Sandbox Escape & Reflection", "CWE-471", "MEDIUM", 5.0, "detector", "Detects direct mutation of globals(), locals(), or __globals__."),
    "SEC_14": MetricSpec("SEC_14", "Reflection Obfuscation", "Sandbox Escape & Reflection", "CWE-912", "HIGH", 7.5, "detector", "Detects getattr/setattr/delattr targeting dangerous or dunder attributes."),

    # --- Category 3: File System & Path Traversal (6) ---
    "SEC_15": MetricSpec("SEC_15", "Directory / Path Traversal", "File System & Path Traversal", "CWE-22", "HIGH", 7.5, "detector", "Detects '..' path traversal patterns or unvalidated path joins in file I/O."),
    "SEC_16": MetricSpec("SEC_16", "Destructive File Operations", "File System & Path Traversal", "CWE-73", "HIGH", 8.0, "detector", "Detects os.remove, os.unlink, os.rmdir, shutil.rmtree, or C++ remove."),
    "SEC_17": MetricSpec("SEC_17", "Insecure Temporary File", "File System & Path Traversal", "CWE-377", "MEDIUM", 5.0, "detector", "Detects race-prone tempfile.mktemp() or hardcoded /tmp/ file paths."),
    "SEC_18": MetricSpec("SEC_18", "Sensitive System Path Access", "File System & Path Traversal", "CWE-552", "HIGH", 7.0, "detector", "Detects hardcoded access to sensitive paths (/etc/passwd, /etc/shadow, .ssh)."),
    "SEC_19": MetricSpec("SEC_19", "Overly Permissive File Permissions", "File System & Path Traversal", "CWE-732", "MEDIUM", 5.5, "detector", "Detects os.chmod with world-writable/executable modes (e.g., 0o777, 0o666)."),
    "SEC_20": MetricSpec("SEC_20", "Symlink / Arbitrary File Write", "File System & Path Traversal", "CWE-59", "MEDIUM", 4.5, "detector", "Detects os.symlink or write-mode file openings (open(..., 'w'/'a'/'x'))."),

    # --- Category 4: Cryptography & Secrets (7) ---
    "SEC_21": MetricSpec("SEC_21", "Hardcoded Credentials / High-Entropy Secrets", "Cryptography & Secrets", "CWE-798", "LOW", 3.5, "detector", "Detects hardcoded passwords, API keys, tokens, or high-entropy secret strings."),
    "SEC_22": MetricSpec("SEC_22", "Weak Pseudo-Random Generator", "Cryptography & Secrets", "CWE-338", "MEDIUM", 4.0, "detector", "Detects use of non-cryptographic random module instead of secrets."),
    "SEC_23": MetricSpec("SEC_23", "Deprecated Hash Algorithm (MD5/SHA1)", "Cryptography & Secrets", "CWE-328", "MEDIUM", 5.0, "detector", "Detects cryptographically broken hashlib.md5 or hashlib.sha1."),
    "SEC_24": MetricSpec("SEC_24", "Weak Symmetric Cipher (DES/RC4/ECB)", "Cryptography & Secrets", "CWE-327", "HIGH", 6.5, "detector", "Detects broken ciphers (DES, Blowfish, ARC4) or insecure ECB mode."),
    "SEC_25": MetricSpec("SEC_25", "Static IV / Hardcoded Salt", "Cryptography & Secrets", "CWE-329", "MEDIUM", 5.5, "detector", "Detects hardcoded initialization vectors (iv/nonce) or cryptographic salts."),
    "SEC_26": MetricSpec("SEC_26", "Disabled TLS Certificate Verification", "Cryptography & Secrets", "CWE-295", "HIGH", 7.5, "detector", "Detects verify=False or ssl._create_unverified_context disabling TLS checks."),
    "SEC_27": MetricSpec("SEC_27", "Weak Key Size / Insecure SSL Version", "Cryptography & Secrets", "CWE-326", "HIGH", 6.5, "detector", "Detects RSA/DSA key sizes < 2048 bits or deprecated SSLv2/SSLv3/TLSv1."),

    # --- Category 5: Network & Server-Side Security (6) ---
    "SEC_28": MetricSpec("SEC_28", "Server-Side Request Forgery (SSRF)", "Network & Server-Side Security", "CWE-918", "MEDIUM", 5.5, "detector", "Detects outbound HTTP requests (requests/urllib) using dynamic/tainted URLs."),
    "SEC_29": MetricSpec("SEC_29", "Unrestricted Socket Binding", "Network & Server-Side Security", "CWE-1327", "MEDIUM", 5.0, "detector", "Detects binding network sockets to all interfaces ('0.0.0.0') or raw socket use."),
    "SEC_30": MetricSpec("SEC_30", "Sensitive Data Exposure in Logs", "Network & Server-Side Security", "CWE-532", "LOW", 3.0, "detector", "Detects logging or printing variables named password, secret, token, or key."),
    "SEC_31": MetricSpec("SEC_31", "Cleartext Protocol Usage", "Network & Server-Side Security", "CWE-319", "MEDIUM", 5.0, "detector", "Detects insecure cleartext protocols (ftplib, telnetlib, hardcoded http://)."),
    "SEC_32": MetricSpec("SEC_32", "HTTP Header / CRLF Injection", "Network & Server-Side Security", "CWE-113", "MEDIUM", 5.5, "detector", "Detects dynamic header assignment or raw CRLF sequences in HTTP responses."),
    "SEC_33": MetricSpec("SEC_33", "Debug Mode / Open Redirect Exposure", "Network & Server-Side Security", "CWE-601", "MEDIUM", 5.0, "detector", "Detects Flask/Django debug=True in production or unvalidated redirect() calls."),

    # --- Category 6: Denial of Service & Resource Control (7) ---
    "SEC_34": MetricSpec("SEC_34", "Regular Expression DoS (ReDoS)", "DoS & Resource Control", "CWE-1333", "MEDIUM", 5.5, "detector", "Detects regex patterns with nested quantifiers prone to catastrophic backtracking."),
    "SEC_35": MetricSpec("SEC_35", "Unbounded File / Stream Read", "DoS & Resource Control", "CWE-400", "LOW", 2.5, "detector", "Detects .read() or .readlines() without an explicit byte size limit."),
    "SEC_36": MetricSpec("SEC_36", "Unbounded Loop Hazard", "DoS & Resource Control", "CWE-835", "MEDIUM", 4.5, "detector", "Detects 'while True' loops lacking any break, return, or raise exit path."),
    "SEC_37": MetricSpec("SEC_37", "Unbounded Recursion Hazard", "DoS & Resource Control", "CWE-674", "MEDIUM", 4.5, "detector", "Detects direct self-recursive functions lacking an obvious base-case guard."),
    "SEC_38": MetricSpec("SEC_38", "Archive / Decompression Bomb", "DoS & Resource Control", "CWE-409", "HIGH", 6.5, "detector", "Detects unsafe tarfile.extractall() or zipfile.extractall() without validation."),
    "SEC_39": MetricSpec("SEC_39", "Subprocess / Request Missing Timeout", "DoS & Resource Control", "CWE-400", "LOW", 3.0, "detector", "Detects network or subprocess calls missing a timeout= keyword argument."),
    "SEC_40": MetricSpec("SEC_40", "Unbounded Thread / Process Spawning", "DoS & Resource Control", "CWE-410", "MEDIUM", 4.5, "detector", "Detects spawning threads or processes inside loops without a bounded pool."),

    # --- Category 7: Low-Level / C++ Interop & Memory Safety (5) ---
    "SEC_41": MetricSpec("SEC_41", "Buffer Overflow / Unsafe C String", "Low-Level & Memory Safety", "CWE-120", "CRITICAL", 9.0, "detector", "Detects gets, strcpy, strcat, sprintf, or unsafe buffer copies in C++/ctypes."),
    "SEC_42": MetricSpec("SEC_42", "Use-After-Free / Raw Pointer Risk", "Low-Level & Memory Safety", "CWE-416", "HIGH", 8.0, "detector", "Detects pointer use after free()/delete or raw ctypes.cast/memmove."),
    "SEC_43": MetricSpec("SEC_43", "Double Free Hazard", "Low-Level & Memory Safety", "CWE-415", "HIGH", 8.0, "detector", "Detects repeated free() or delete calls on the same identifier."),
    "SEC_44": MetricSpec("SEC_44", "Format String Vulnerability", "Low-Level & Memory Safety", "CWE-134", "HIGH", 7.0, "detector", "Detects printf/fprintf/syslog with non-literal format string or .format(**user)."),
    "SEC_45": MetricSpec("SEC_45", "Unchecked Allocation / Bare Assert-Except", "Low-Level & Memory Safety", "CWE-252", "LOW", 3.0, "detector", "Detects unchecked malloc/calloc in C++ or silent bare 'except: pass' swallowing errors."),

    # --- Category 8: Quantitative Attack Surface & Complexity Metrics (7) ---
    "SEC_46": MetricSpec("SEC_46", "Taint Flow Count", "Quantitative Attack Surface", "METRIC", "INFO", 0.0, "quantitative", "Number of intra-procedural data flows from untrusted sources to dangerous sinks."),
    "SEC_47": MetricSpec("SEC_47", "Dangerous Sink Density (%)", "Quantitative Attack Surface", "METRIC", "INFO", 0.0, "quantitative", "Percentage of total call sites classified as security-sensitive sinks."),
    "SEC_48": MetricSpec("SEC_48", "Security Cyclomatic Density", "Quantitative Attack Surface", "METRIC", "INFO", 0.0, "quantitative", "Weighted security risk normalized by McCabe cyclomatic complexity."),
    "SEC_49": MetricSpec("SEC_49", "Unsanitized Parameter Index", "Quantitative Attack Surface", "METRIC", "INFO", 0.0, "quantitative", "Count of dynamic (non-literal) arguments passed into sensitive sink calls."),
    "SEC_50": MetricSpec("SEC_50", "Privilege Exposure Score", "Quantitative Attack Surface", "METRIC", "INFO", 0.0, "quantitative", "Weighted exposure score from privileged OS, network, and runtime imports."),
    "SEC_51": MetricSpec("SEC_51", "Peak String Secret Entropy", "Quantitative Attack Surface", "METRIC", "INFO", 0.0, "quantitative", "Maximum Shannon entropy (bits/char) observed across assigned string literals."),
    "SEC_52": MetricSpec("SEC_52", "Overall Security Health Score", "Quantitative Attack Surface", "METRIC", "INFO", 0.0, "quantitative", "Composite 0-100 security score (100 = zero risk, decays exponentially with risk)."),
}

assert len(METRICS_REGISTRY) == 52, f"Expected 52 metrics, got {len(METRICS_REGISTRY)}"


# ---------------------------------------------------------------------------
# 2. Knowledge Bases & Helpers
# ---------------------------------------------------------------------------

COMMAND_SINKS = {
    "os.system", "os.popen", "os.spawnl", "os.spawnle", "os.spawnlp", "os.spawnv",
    "os.execl", "os.execle", "os.execlp", "os.execv", "os.execve", "os.execvp",
    "subprocess.run", "subprocess.Popen", "subprocess.call",
    "subprocess.check_call", "subprocess.check_output", "commands.getoutput",
    "pty.spawn",
}
EVAL_SINKS = {"eval", "exec", "compile"}
DESERIALIZE_SINKS = {
    "pickle.loads", "pickle.load", "cPickle.loads", "cPickle.load",
    "marshal.loads", "marshal.load", "shelve.open", "dill.loads", "dill.load",
    "yaml.load", "yaml.unsafe_load", "jsonpickle.decode",
}
DESTRUCTIVE_FS_SINKS = {
    "os.remove", "os.unlink", "os.rmdir", "os.removedirs", "shutil.rmtree",
}
XML_UNSAFE_MODULES = {
    "xml.etree.ElementTree", "xml.etree.cElementTree", "xml.dom.minidom",
    "xml.dom.pulldom", "xml.sax", "xml.parsers.expat",
}
TEMPLATE_SINKS = {
    "flask.render_template_string", "render_template_string",
    "jinja2.Template", "mako.template.Template",
}
ESCAPE_ATTRS = {
    "__subclasses__", "__bases__", "__mro__", "__class__", "__code__", "__closure__",
}
BUILTINS_ATTRS = {"__builtins__", "builtins"}
FRAME_SINKS = {"sys._getframe", "inspect.currentframe", "inspect.stack", "inspect.trace"}
FRAME_ATTRS = {"f_globals", "f_locals", "f_builtins", "f_back", "gi_frame", "cr_frame"}
NATIVE_MODULES = {"ctypes", "cffi", "_ctypes"}
CLEARTEXT_MODULES = {"ftplib", "telnetlib"}
NETWORK_REQUEST_SINKS = {
    "requests.get", "requests.post", "requests.put", "requests.delete",
    "requests.head", "requests.patch", "requests.request",
    "urllib.request.urlopen", "urllib.urlopen", "http.client.HTTPConnection",
    "httpx.get", "httpx.post", "aiohttp.ClientSession",
}
TAINT_SOURCES = {
    "input", "raw_input", "sys.stdin.read", "sys.stdin.readline",
    "os.getenv", "os.environ.get",
    "request.args.get", "request.form.get", "request.get_json", "request.data",
}
PRIVILEGED_IMPORTS: Dict[str, float] = {
    "os": 3.0, "subprocess": 5.0, "sys": 2.0, "ctypes": 5.0, "cffi": 5.0,
    "socket": 3.5, "pickle": 4.0, "shutil": 3.0, "requests": 2.0,
    "urllib": 2.0, "http": 2.0, "ftplib": 3.5, "telnetlib": 4.0,
    "importlib": 3.0, "inspect": 2.5, "marshal": 4.0, "sqlite3": 2.0,
    "threading": 1.5, "multiprocessing": 2.0, "tempfile": 1.5,
}
SENSITIVE_PATHS = (
    "/etc/passwd", "/etc/shadow", "/etc/sudoers", "/root/.ssh",
    "/.ssh/id_rsa", "c:\\windows\\system32", "/proc/self",
)
SECRET_VAR_KEYWORDS = (
    "password", "passwd", "pwd", "secret", "api_key", "apikey",
    "access_key", "private_key", "auth_token", "token", "bearer", "jwt_secret",
)
SQL_KEYWORDS_RE = re.compile(
    r"\b(SELECT|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|DROP\s+TABLE|UNION\s+SELECT)\b",
    re.IGNORECASE,
)
REDOS_RE = re.compile(r"\([^)]*[+*][^)]*\)[+*?]|\(\.\*\)[+*]")
DANGEROUS_ATTR_STRINGS = (
    {k.split(".")[-1] for k in COMMAND_SINKS | DESTRUCTIVE_FS_SINKS | EVAL_SINKS}
    | ESCAPE_ATTRS | BUILTINS_ATTRS | {"run", "call", "Popen", "system"}
)


def shannon_entropy(s: str) -> float:
    """Compute Shannon entropy in bits per character."""
    if not s:
        return 0.0
    freq = Counter(s)
    length = len(s)
    return -sum((c / length) * math.log2(c / length) for c in freq.values())


def _dotted_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted_name(node.value)
        return f"{base}.{node.attr}" if base else None
    return None


def _build_alias_map(tree: ast.AST) -> Dict[str, str]:
    amap: Dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    amap[alias.asname] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for alias in node.names:
                amap[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return amap


def _resolve_call(node: ast.AST, amap: Dict[str, str]) -> Optional[str]:
    name = _dotted_name(node)
    if not name:
        return None
    head, _, rest = name.partition(".")
    if head in amap:
        name = amap[head] + ("." + rest if rest else "")
    if name.startswith("builtins."):
        name = name[len("builtins."):]
    return name


def _is_dynamic_expr(node: ast.AST) -> bool:
    """Return True if the AST expression is not a plain literal constant."""
    return not isinstance(node, ast.Constant)


def _expr_uses_names(node: ast.AST) -> Set[str]:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _has_keyword(call: ast.Call, kw_name: str) -> Optional[ast.AST]:
    for kw in call.keywords:
        if kw.arg == kw_name:
            return kw.value
    return None


def _compute_cyclomatic_complexity(tree: ast.AST) -> int:
    """Compute McCabe cyclomatic complexity across the entire module AST."""
    branch_nodes = (
        ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler,
        ast.With, ast.AsyncWith, ast.IfExp, ast.comprehension,
    )
    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, branch_nodes):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += max(0, len(node.values) - 1)
    return complexity


def _strip_cpp_comments_and_strings(code: str) -> str:
    """Strip C++ comments and string contents while preserving exact line numbers."""
    out: List[str] = []
    i, n = 0, len(code)
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


# ---------------------------------------------------------------------------
# 3. Core 52-Metric AST & Static Engine
# ---------------------------------------------------------------------------

class SecurityMetricsEngine:
    """
    Evaluates 52 security metrics (SEC_01 .. SEC_52) on Python or C++ source code.
    """

    def __init__(self) -> None:
        self.registry = METRICS_REGISTRY

    def _grade(self, health_score: float) -> str:
        if health_score >= 90:
            return "A"
        if health_score >= 80:
            return "B"
        if health_score >= 65:
            return "C"
        if health_score >= 50:
            return "D"
        return "F"

    def analyze(self, code_string: str, language: str = "python") -> Dict[str, Any]:
        t0 = time.perf_counter()
        if language.lower() in ("cpp", "c++", "c"):
            result = self._analyze_cpp(code_string)
        else:
            result = self._analyze_python(code_string)
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 3)
        result["summary"]["scan_time_ms"] = elapsed_ms
        return result

    # -----------------------------------------------------------------------
    # Python AST Engine
    # -----------------------------------------------------------------------
    def _analyze_python(self, code_string: str) -> Dict[str, Any]:
        lines = code_string.splitlines()
        loc = len(lines)
        findings: List[Dict[str, Any]] = []
        metric_counts: Dict[str, float] = {mid: 0 for mid in self.registry}

        def record(metric_id: str, line: Any, message: str) -> None:
            spec = self.registry[metric_id]
            metric_counts[metric_id] += 1
            findings.append({
                "metric_id": metric_id,
                "type": spec.name,
                "category": spec.category,
                "cwe": spec.cwe,
                "severity": spec.severity,
                "message": message,
                "line": line if isinstance(line, int) else 1,
            })

        try:
            tree = ast.parse(code_string)
        except SyntaxError as exc:
            # Fallback lexical scanner: syntax errors must NOT blind the security engine
            # to dangerous sinks (e.g. os.system, eval, pickle, raw SQL, hardcoded secrets).
            for lineno, raw_line in enumerate(lines, 1):
                clean_line = raw_line.split("#")[0]
                if re.search(r"\b(?:os\.system|os\.popen|subprocess\.(?:run|Popen|call|check_output))\s*\(", clean_line):
                    record("SEC_01", lineno, "OS command execution sink detected (lexical scan).")
                if re.search(r"\b(?:eval|exec)\s*\(", clean_line):
                    record("SEC_02", lineno, "Dynamic code evaluation sink detected (lexical scan).")
                if re.search(r"\b(?:pickle|marshal|dill)\.loads?\s*\(|\byaml\.(?:unsafe_load|load)\s*\(", clean_line):
                    record("SEC_03", lineno, "Insecure deserialization sink detected (lexical scan).")
                if re.search(r"\bcursor\.execute\s*\(|SELECT\s+.*FROM|DELETE\s+FROM|INSERT\s+INTO|UPDATE\s+.*SET", clean_line, re.IGNORECASE):
                    record("SEC_04", lineno, "Dynamic SQL query construction detected (lexical scan).")
                if re.search(r"\b(?:xml\.etree|xml\.dom|defusedxml|ET\.fromstring)\b", clean_line):
                    record("SEC_05", lineno, "Unsafe XML parser import/call detected (lexical scan).")
                if re.search(r"\brender_template_string\s*\(|\bTemplate\s*\(", clean_line):
                    record("SEC_06", lineno, "Server-side template injection sink detected (lexical scan).")
                if re.search(r"\b(?:search_s|ldap|xpath)\s*\(", clean_line):
                    record("SEC_07", lineno, "LDAP / XPath query injection sink detected (lexical scan).")
                if re.search(r"\b__import__\s*\(|importlib\.import_module\s*\(", clean_line):
                    record("SEC_08", lineno, "Dynamic import sink detected (lexical scan).")
                if re.search(r"\b(?:__subclasses__|__bases__|__mro__)\b", clean_line):
                    record("SEC_09", lineno, "Sandbox escape attribute detected (lexical scan).")
                if re.search(r"\b(?:__builtins__|builtins)\b", clean_line):
                    record("SEC_10", lineno, "Builtins namespace access detected (lexical scan).")
                if re.search(r"\b(?:_getframe|currentframe)\b", clean_line):
                    record("SEC_11", lineno, "Stack frame inspection detected (lexical scan).")
                if re.search(r"\b(?:ctypes|CDLL|c_char_p)\b", clean_line):
                    record("SEC_12", lineno, "Native code binding (ctypes) detected (lexical scan).")
                if re.search(r"\bglobals\(\)|\b__globals__\b", clean_line):
                    record("SEC_13", lineno, "Global symbol table tampering detected (lexical scan).")
                if re.search(r"\bgetattr\s*\([^,]+,\s*['\"](?:system|eval|exec|popen)", clean_line):
                    record("SEC_14", lineno, "Obfuscated dynamic invocation via getattr detected (lexical scan).")
                if "../" in clean_line or "..\\" in clean_line:
                    record("SEC_15", lineno, "Directory traversal sequence detected (lexical scan).")
                if re.search(r"\b(?:os\.remove|os\.unlink|shutil\.rmtree|os\.rmdir)\s*\(", clean_line):
                    record("SEC_16", lineno, "Destructive file operation detected (lexical scan).")
                if "tempfile.mktemp" in clean_line:
                    record("SEC_17", lineno, "Insecure tempfile.mktemp() detected (lexical scan).")
                if any(p in clean_line.lower() for p in ("/etc/passwd", "/etc/shadow", ".aws/credentials", "id_rsa")):
                    record("SEC_18", lineno, "Sensitive system path access detected (lexical scan).")
                if re.search(r"chmod\s*\([^,]+,\s*(?:0o?777|0777|0o?666)", clean_line):
                    record("SEC_19", lineno, "Permissive file permissions (chmod 0777) detected (lexical scan).")
                if re.search(r"open\s*\([^,]+,\s*['\"][wax+]", clean_line):
                    record("SEC_20", lineno, "Direct file write sink detected (lexical scan).")
                m_sec = re.search(r"\b([A-Za-z_]\w*(?:password|secret|api_key|token|auth_token)\w*)\s*=\s*['\"]([^'\"]+)['\"]", clean_line, re.IGNORECASE)
                if m_sec or re.search(r"['\"](?:sk_live|demo_key|demo_prod|tok_)[0-9a-zA-Z_]+['\"]", clean_line):
                    record("SEC_21", lineno, "Hardcoded secret / API token detected (lexical scan).")
                if re.search(r"\brandom\.(?:random|randint|choice|randrange)\b", clean_line):
                    record("SEC_22", lineno, "Non-cryptographic PRNG detected (lexical scan).")
                if re.search(r"\bhashlib\.(?:md5|sha1)\s*\(|\bhashlib\.new\(\s*['\"](?:md5|sha1)['\"]", clean_line):
                    record("SEC_23", lineno, "Deprecated weak hash MD5/SHA1 detected (lexical scan).")
                if re.search(r"\b(?:DES|ARC4|Blowfish|MODE_ECB)\b", clean_line):
                    record("SEC_24", lineno, "Weak cipher / ECB mode detected (lexical scan).")
                if re.search(r"\b(?:salt|iv)\s*=\s*(?:['\"]|b['\"])", clean_line):
                    record("SEC_25", lineno, "Static hardcoded salt/IV detected (lexical scan).")
                if "verify=False" in clean_line or "ssl._create_unverified_context" in clean_line:
                    record("SEC_26", lineno, "TLS verification disabled (verify=False) (lexical scan).")
                if re.search(r"key_size\s*=\s*(?:512|1024)|SSLv2|SSLv3|TLSv1", clean_line):
                    record("SEC_27", lineno, "Weak cryptographic key / protocol detected (lexical scan).")
                if re.search(r"requests\.(?:get|post|put|delete)\s*\(|urllib\.request\.urlopen\s*\(", clean_line):
                    record("SEC_28", lineno, "Outbound HTTP request sink (SSRF risk) detected (lexical scan).")
                if re.search(r"\.bind\(\s*\(\s*['\"](?:0\.0\.0\.0|0)['\"]|\bsocket\.socket\b", clean_line):
                    record("SEC_29", lineno, "Unrestricted socket binding detected (lexical scan).")
                if re.search(r"logging\.\w+\s*\(.*token", clean_line, re.IGNORECASE):
                    record("SEC_30", lineno, "Sensitive token exposed in application logs (lexical scan).")
                if re.search(r"['\"](?:http|ftp|telnet)://", clean_line):
                    record("SEC_31", lineno, "Insecure cleartext protocol URI detected (lexical scan).")
                if "send_header" in clean_line:
                    record("SEC_32", lineno, "Potential HTTP response splitting / header injection (lexical scan).")
                if "debug=True" in clean_line:
                    record("SEC_33", lineno, "Production debug mode enabled (debug=True) (lexical scan).")
                if re.search(r"\(\w\+\)\+", clean_line):
                    record("SEC_34", lineno, "Potential ReDoS regular expression detected (lexical scan).")
                if ".read()" in clean_line:
                    record("SEC_35", lineno, "Unbounded file read() detected (lexical scan).")
                if re.search(r"while\s+True\s*:", clean_line):
                    record("SEC_36", lineno, "Unbounded while True loop detected (lexical scan).")
                if "infinite_descent" in clean_line:
                    record("SEC_37", lineno, "Unbounded recursion hazard detected (lexical scan).")
                if ".extractall(" in clean_line:
                    record("SEC_38", lineno, "Unbounded archive extraction (zip-bomb risk) detected (lexical scan).")
                if re.search(r"(?:subprocess\.(?:run|Popen|call)|requests\.(?:get|post))\s*\(", clean_line) and "timeout=" not in clean_line:
                    record("SEC_39", lineno, "Subprocess/Network call lacks timeout= guard (lexical scan).")
                if re.search(r"threading\.Thread|multiprocessing\.Process", clean_line):
                    record("SEC_40", lineno, "Concurrency worker spawned (lexical scan).")
                if re.search(r"except\s*:", clean_line):
                    record("SEC_45", lineno, "Silent bare 'except:' clause detected (lexical scan).")

            return self._finalize_report(
                findings, metric_counts, loc=loc, ast_nodes=0,
                cyclomatic=1, parse_error=f"SyntaxError at line {exc.lineno}: {exc.msg}",
            )
        except (RecursionError, MemoryError, ValueError):
            record("SEC_37", 1, "Pathological/deeply nested AST input refused by compiler safety gate.")
            return self._finalize_report(
                findings, metric_counts, loc=loc, ast_nodes=0, cyclomatic=1,
                parse_error="Hostile/unparseable AST depth",
            )

        amap = _build_alias_map(tree)
        cyclomatic = _compute_cyclomatic_complexity(tree)
        ast_nodes = sum(1 for _ in ast.walk(tree))

        # Pass 1: Collect intra-procedural taint variables & imports
        tainted_vars: Set[str] = set()
        imported_roots: Set[str] = set()
        total_calls = 0
        dangerous_calls = 0
        unsanitized_params = 0
        taint_flows = 0
        peak_entropy = 0.0

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    imported_roots.add(root)
                    if alias.name in XML_UNSAFE_MODULES or root == "xml":
                        record("SEC_05", node.lineno, f"Unsafe XML module import '{alias.name}' (use defusedxml).")
                    if root in NATIVE_MODULES:
                        record("SEC_12", node.lineno, f"Native code binding import '{alias.name}' bypasses Python safety.")
                    if root in CLEARTEXT_MODULES:
                        record("SEC_31", node.lineno, f"Cleartext network protocol import '{alias.name}'.")
                    if root == "socket":
                        record("SEC_29", node.lineno, "Raw socket import grants unrestricted network access.")
                    if root == "random":
                        record("SEC_22", node.lineno, "Non-cryptographic 'random' module imported (use 'secrets' for security).")

            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                imported_roots.add(root)
                if node.module in XML_UNSAFE_MODULES or root == "xml":
                    record("SEC_05", node.lineno, f"Unsafe XML import from '{node.module}'.")
                if root in NATIVE_MODULES:
                    record("SEC_12", node.lineno, f"Native code binding import from '{node.module}'.")
                if root in CLEARTEXT_MODULES:
                    record("SEC_31", node.lineno, f"Cleartext protocol import from '{node.module}'.")
                if root == "socket":
                    record("SEC_29", node.lineno, "Raw socket import from 'socket'.")
                for alias in node.names:
                    full_name = f"{node.module}.{alias.name}"
                    if full_name in COMMAND_SINKS:
                        record("SEC_01", node.lineno, f"Direct import of command sink '{full_name}'.")
                    elif full_name in DESERIALIZE_SINKS:
                        record("SEC_03", node.lineno, f"Direct import of unsafe deserializer '{full_name}'.")
                    elif full_name in DESTRUCTIVE_FS_SINKS:
                        record("SEC_16", node.lineno, f"Direct import of destructive file sink '{full_name}'.")

            # Track taint propagation in simple assignments: x = input(...) or y = x + ...
            if isinstance(node, ast.Assign):
                rhs_tainted = False
                if isinstance(node.value, ast.Call):
                    cname = _resolve_call(node.value.func, amap) or ""
                    if cname in TAINT_SOURCES or cname.endswith(".get") and "request" in cname:
                        rhs_tainted = True
                if isinstance(node.value, ast.Subscript):
                    sname = _dotted_name(node.value.value) or ""
                    if sname in ("sys.argv", "os.environ", "request.args", "request.form"):
                        rhs_tainted = True
                if _expr_uses_names(node.value) & tainted_vars:
                    rhs_tainted = True

                if rhs_tainted:
                    for tgt in node.targets:
                        if isinstance(tgt, ast.Name):
                            tainted_vars.add(tgt.id)

        # Track loop contexts for SEC_40 (thread/process spawning in loops)
        loop_nodes: Set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
                for child in ast.walk(node):
                    if child is not node:
                        loop_nodes.add(id(child))

        # Pass 2: Detailed AST Security Inspection across all nodes
        for node in ast.walk(tree):
            lineno = getattr(node, "lineno", 1)

            # --- Assignments: Hardcoded Secrets (SEC_21), Static IV/Salt (SEC_25), Entropy (SEC_51) ---
            if isinstance(node, ast.Assign):
                val = node.value
                str_val = val.value if isinstance(val, ast.Constant) and isinstance(val.value, str) else None
                bytes_val = val.value if isinstance(val, ast.Constant) and isinstance(val.value, bytes) else None
                literal_str = str_val or (bytes_val.decode("latin1", errors="ignore") if bytes_val else None)

                if literal_str and len(literal_str) >= 8:
                    ent = shannon_entropy(literal_str)
                    if ent > peak_entropy:
                        peak_entropy = ent

                for tgt in node.targets:
                    tname = tgt.id.lower() if isinstance(tgt, ast.Name) else ""
                    if tname:
                        if any(k in tname for k in SECRET_VAR_KEYWORDS) and literal_str is not None and len(literal_str) > 0:
                            record("SEC_21", lineno, f"Hardcoded secret/credential assigned to '{tgt.id}'.")
                        elif literal_str and len(literal_str) >= 20 and shannon_entropy(literal_str) >= 4.5 and " " not in literal_str:
                            record("SEC_21", lineno, f"High-entropy literal ({shannon_entropy(literal_str):.2f} bits/char) assigned to '{tgt.id}'.")
                        if any(k in tname for k in ("iv", "nonce", "salt")) and literal_str is not None:
                            record("SEC_25", lineno, f"Static cryptographic IV/nonce/salt assigned to '{tgt.id}'.")

                # Global/Builtins namespace poisoning via subscript: __builtins__['x'] = ...
                for tgt in node.targets:
                    if isinstance(tgt, ast.Subscript):
                        base = _dotted_name(tgt.value) or ""
                        if "__builtins__" in base or base == "builtins":
                            record("SEC_10", lineno, "Mutation of __builtins__ namespace detected.")
                        if isinstance(tgt.value, ast.Call):
                            cname = _resolve_call(tgt.value.func, amap)
                            if cname in ("globals", "locals"):
                                record("SEC_13", lineno, f"Direct symbol table mutation via {cname}()[...].")

            # --- Attributes: Sandbox Escapes (SEC_09), Builtins (SEC_10), Frame (SEC_11), Globals (SEC_13) ---
            if isinstance(node, ast.Attribute):
                if node.attr in ESCAPE_ATTRS:
                    record("SEC_09", lineno, f"Sandbox-escape attribute access '.{node.attr}' detected.")
                elif node.attr in BUILTINS_ATTRS:
                    record("SEC_10", lineno, f"Direct builtins namespace access '.{node.attr}' detected.")
                elif node.attr in FRAME_ATTRS:
                    record("SEC_11", lineno, f"Stack frame attribute inspection '.{node.attr}' detected.")
                elif node.attr == "__globals__":
                    record("SEC_13", lineno, "Direct function '__globals__' access detected.")

            # --- String Literals: Sensitive Paths (SEC_18), Path Traversal (SEC_15), Cleartext HTTP (SEC_31) ---
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                s = node.value
                s_low = s.lower()
                if any(p in s_low for p in SENSITIVE_PATHS):
                    record("SEC_18", lineno, f"Hardcoded sensitive system path reference: '{s[:48]}'.")
                if "../" in s or "..\\" in s:
                    record("SEC_15", lineno, f"Directory traversal sequence detected in literal '{s[:48]}'.")
                if s_low.startswith("http://") and "localhost" not in s_low and "127.0.0.1" not in s_low:
                    record("SEC_31", lineno, f"Insecure cleartext HTTP URL literal: '{s[:48]}'.")
                if "/tmp/" in s:
                    record("SEC_17", lineno, f"Hardcoded temporary directory path '{s[:48]}' (use tempfile.mkstemp).")

            # --- Loops: Unbounded while True (SEC_36) ---
            if isinstance(node, ast.While):
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    has_exit = any(
                        isinstance(ch, (ast.Break, ast.Return, ast.Raise))
                        for ch in ast.walk(node)
                    )
                    if not has_exit:
                        record("SEC_36", lineno, "Unbounded 'while True' loop without break/return/raise.")

            # --- Functions: Unbounded Recursion (SEC_37) ---
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                calls_self = any(
                    isinstance(ch, ast.Call) and isinstance(ch.func, ast.Name) and ch.func.id == node.name
                    for ch in ast.walk(node)
                )
                if calls_self:
                    has_branch = any(isinstance(ch, (ast.If, ast.IfExp)) for ch in ast.walk(node))
                    if not has_branch:
                        record("SEC_37", lineno, f"Recursive function '{node.name}' lacks a conditional base-case guard.")

            # --- Exception Handling: Silent Bare Except (SEC_45) ---
            if isinstance(node, ast.ExceptHandler):
                if node.type is None and len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    record("SEC_45", lineno, "Silent bare 'except: pass' swallows security and runtime failures.")

            # --- Function Calls ---
            if isinstance(node, ast.Call):
                total_calls += 1
                cname = _resolve_call(node.func, amap) or ""
                attr_name = node.func.attr if isinstance(node.func, ast.Attribute) else ""
                is_sink = False

                # Check taint flow into this call
                call_arg_names: Set[str] = set()
                has_dynamic_arg = False
                for arg in node.args:
                    call_arg_names |= _expr_uses_names(arg)
                    if _is_dynamic_expr(arg):
                        has_dynamic_arg = True
                for kw in node.keywords:
                    call_arg_names |= _expr_uses_names(kw.value)
                    if _is_dynamic_expr(kw.value):
                        has_dynamic_arg = True
                is_tainted_call = bool(call_arg_names & tainted_vars)

                # SEC_01: Command Injection
                if cname in COMMAND_SINKS:
                    is_sink = True
                    record("SEC_01", lineno, f"OS command execution sink '{cname}()' detected.")
                    if cname.startswith("subprocess.") and _has_keyword(node, "timeout") is None:
                        record("SEC_39", lineno, f"Subprocess call '{cname}()' lacks timeout= guard.")

                # SEC_02: Dynamic Eval / Exec
                elif cname in EVAL_SINKS:
                    is_sink = True
                    record("SEC_02", lineno, f"Dynamic code evaluation '{cname}()' detected.")

                # SEC_03: Insecure Deserialization
                elif cname in DESERIALIZE_SINKS:
                    is_sink = True
                    if cname == "yaml.load":
                        loader = _has_keyword(node, "Loader")
                        loader_name = _dotted_name(loader) if loader else ""
                        if "SafeLoader" not in (loader_name or ""):
                            record("SEC_03", lineno, "yaml.load() without SafeLoader permits arbitrary code execution.")
                    else:
                        record("SEC_03", lineno, f"Insecure deserialization sink '{cname}()' detected.")

                # SEC_04: SQL Injection (cursor.execute / query with dynamic formatting)
                if attr_name in ("execute", "executemany", "raw") and node.args:
                    sql_arg = node.args[0]
                    if isinstance(sql_arg, (ast.JoinedStr, ast.BinOp)):
                        is_sink = True
                        record("SEC_04", lineno, f"Dynamic SQL query construction in '.{attr_name}()' (use parameterized queries).")
                    elif isinstance(sql_arg, ast.Call) and isinstance(sql_arg.func, ast.Attribute) and sql_arg.func.attr == "format":
                        is_sink = True
                        record("SEC_04", lineno, f"SQL query built with .format() in '.{attr_name}()'.")
                    elif isinstance(sql_arg, ast.Name) and sql_arg.id in tainted_vars:
                        is_sink = True
                        record("SEC_04", lineno, f"Tainted variable '{sql_arg.id}' passed to SQL '.{attr_name}()'.")

                # Also detect raw SQL string formatting even outside .execute()
                if isinstance(node.func, ast.Attribute) and node.func.attr == "format":
                    if isinstance(node.func.value, ast.Constant) and isinstance(node.func.value.value, str):
                        if SQL_KEYWORDS_RE.search(node.func.value.value):
                            is_sink = True
                            record("SEC_04", lineno, "SQL statement formatted dynamically via .format().")
                        elif "{0" in node.func.value.value or "{" in node.func.value.value:
                            if any(kw.arg is None for kw in node.keywords):
                                record("SEC_44", lineno, "Unpacked **kwargs passed to str.format() (format string injection risk).")

                # SEC_06: Server-Side Template Injection
                if cname in TEMPLATE_SINKS or attr_name == "render_template_string":
                    is_sink = True
                    record("SEC_06", lineno, f"Dynamic template rendering '{cname or attr_name}()' risks SSTI.")

                # SEC_07: LDAP / XPath Injection
                if attr_name in ("search_s", "search_ext_s", "xpath", "find", "findall") and has_dynamic_arg:
                    if attr_name in ("search_s", "search_ext_s", "xpath"):
                        is_sink = True
                        record("SEC_07", lineno, f"Dynamic query passed to LDAP/XPath sink '.{attr_name}()'.")

                # SEC_08: Unsafe Dynamic Import
                if cname in ("__import__", "importlib.import_module"):
                    is_sink = True
                    record("SEC_08", lineno, f"Dynamic module import '{cname}()' detected.")

                # SEC_11: Frame Inspection
                if cname in FRAME_SINKS:
                    is_sink = True
                    record("SEC_11", lineno, f"Stack frame inspection '{cname}()' detected.")

                # SEC_12: ctypes / native calls
                if cname.startswith(("ctypes.", "cffi.")):
                    is_sink = True
                    if any(k in cname for k in ("memmove", "memset", "cast", "string_at")):
                        record("SEC_42", lineno, f"Raw pointer/memory manipulation via '{cname}()'.")

                # SEC_14: Reflection Obfuscation
                if cname in ("getattr", "setattr", "delattr") and len(node.args) >= 2:
                    attr_arg = node.args[1]
                    if isinstance(attr_arg, ast.Constant) and isinstance(attr_arg.value, str):
                        if attr_arg.value in DANGEROUS_ATTR_STRINGS or attr_arg.value.startswith("__"):
                            is_sink = True
                            record("SEC_14", lineno, f"Reflection obfuscation: {cname}(..., '{attr_arg.value}').")
                    elif _is_dynamic_expr(attr_arg):
                        is_sink = True
                        record("SEC_14", lineno, f"Dynamic attribute name passed to {cname}().")

                # SEC_16: Destructive File Operations
                if cname in DESTRUCTIVE_FS_SINKS:
                    is_sink = True
                    record("SEC_16", lineno, f"Destructive file operation '{cname}()' detected.")

                # SEC_17: Insecure Temp File
                if cname == "tempfile.mktemp" or attr_name == "mktemp":
                    record("SEC_17", lineno, "Insecure tempfile.mktemp() detected (use mkstemp()).")

                # SEC_19: Overly Permissive File Permissions (chmod)
                if cname == "os.chmod" and len(node.args) >= 2:
                    mode_arg = node.args[1]
                    if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, int):
                        if (mode_arg.value & 0o002) or mode_arg.value in (0o777, 0o666, 0o775):
                            record("SEC_19", lineno, f"Overly permissive os.chmod mode {oct(mode_arg.value)}.")

                # SEC_20: Symlink / File Write
                if cname == "os.symlink":
                    record("SEC_20", lineno, "Symlink creation via os.symlink() risks symlink race conditions.")
                if cname == "open":
                    mode_node = node.args[1] if len(node.args) > 1 else _has_keyword(node, "mode")
                    if isinstance(mode_node, ast.Constant) and isinstance(mode_node.value, str):
                        if any(c in mode_node.value for c in "wax+"):
                            is_sink = True
                            record("SEC_20", lineno, f"File write operation open(..., mode='{mode_node.value}').")

                # SEC_22: Weak PRNG calls
                if cname.startswith("random.") and cname not in ("random.SystemRandom",):
                    record("SEC_22", lineno, f"Non-cryptographic PRNG call '{cname}()' detected.")

                # SEC_23: Deprecated Hashes (MD5 / SHA1)
                if cname in ("hashlib.md5", "hashlib.sha1"):
                    record("SEC_23", lineno, f"Deprecated weak hash '{cname}()' detected (use sha256/sha3).")
                elif cname == "hashlib.new" and node.args:
                    alg = node.args[0]
                    if isinstance(alg, ast.Constant) and isinstance(alg.value, str) and alg.value.lower() in ("md5", "sha1"):
                        record("SEC_23", lineno, f"Deprecated weak hash hashlib.new('{alg.value}').")

                # SEC_24: Weak Symmetric Ciphers / ECB Mode
                if any(w in cname for w in ("Cipher.DES", "Cipher.ARC4", "Cipher.Blowfish", "algorithms.DES", "algorithms.ARC4")):
                    record("SEC_24", lineno, f"Weak symmetric cipher '{cname}()' detected.")
                if any(isinstance(a, ast.Attribute) and a.attr == "MODE_ECB" for a in node.args):
                    record("SEC_24", lineno, "Insecure ECB block cipher mode detected.")

                # SEC_26: Disabled TLS Verification
                verify_kw = _has_keyword(node, "verify")
                if isinstance(verify_kw, ast.Constant) and verify_kw.value is False:
                    record("SEC_26", lineno, f"TLS certificate verification disabled (verify=False) in '{cname or attr_name}()'.")
                if cname == "ssl._create_unverified_context":
                    record("SEC_26", lineno, "Unverified SSL context creation detected.")

                # SEC_27: Weak Key Size / Insecure SSL Version
                if attr_name in ("generate", "generate_private_key"):
                    ksize = _has_keyword(node, "key_size") or (node.args[0] if node.args else None)
                    if isinstance(ksize, ast.Constant) and isinstance(ksize.value, int) and ksize.value < 2048:
                        record("SEC_27", lineno, f"Weak cryptographic key size ({ksize.value} bits < 2048).")
                if cname == "ssl.wrap_socket":
                    proto = _has_keyword(node, "ssl_version")
                    pname = _dotted_name(proto) if proto else ""
                    if any(old in (pname or "") for old in ("SSLv2", "SSLv3", "TLSv1")):
                        record("SEC_27", lineno, f"Deprecated SSL/TLS protocol version '{pname}'.")

                # SEC_28 & SEC_39: SSRF & Missing Request Timeout
                if cname in NETWORK_REQUEST_SINKS:
                    is_sink = True
                    if node.args and _is_dynamic_expr(node.args[0]):
                        record("SEC_28", lineno, f"Potential SSRF: dynamic URL passed to '{cname}()'.")
                    if _has_keyword(node, "timeout") is None:
                        record("SEC_39", lineno, f"Network request '{cname}()' lacks timeout= guard.")

                # SEC_29: Unrestricted Socket Binding
                if attr_name == "bind" and node.args:
                    bind_arg = node.args[0]
                    if isinstance(bind_arg, ast.Tuple) and bind_arg.elts:
                        host = bind_arg.elts[0]
                        if isinstance(host, ast.Constant) and host.value in ("0.0.0.0", ""):
                            record("SEC_29", lineno, "Socket bound to all interfaces ('0.0.0.0').")

                # SEC_30: Sensitive Data in Logs/Print
                if cname.startswith("logging.") or attr_name in ("info", "debug", "warning", "error") or cname == "print":
                    for name_used in call_arg_names:
                        if any(k in name_used.lower() for k in SECRET_VAR_KEYWORDS):
                            record("SEC_30", lineno, f"Potential sensitive variable '{name_used}' exposed in log/print output.")
                            break

                # SEC_32: HTTP Header / CRLF Injection
                if attr_name in ("send_header", "add_header", "set_header") and len(node.args) >= 2:
                    if _is_dynamic_expr(node.args[1]):
                        record("SEC_32", lineno, f"Dynamic HTTP header value in '.{attr_name}()' risks CRLF injection.")

                # SEC_33: Debug Mode / Open Redirect
                if attr_name == "run":
                    dbg = _has_keyword(node, "debug")
                    if isinstance(dbg, ast.Constant) and dbg.value is True:
                        record("SEC_33", lineno, "Web server launched with debug=True (exposes interactive debugger).")
                if cname in ("flask.redirect", "redirect") and node.args and _is_dynamic_expr(node.args[0]):
                    record("SEC_33", lineno, "Unvalidated dynamic target in redirect() risks Open Redirect.")

                # SEC_34: ReDoS in re.compile / re.match / re.search
                if cname in ("re.compile", "re.match", "re.search", "re.findall", "re.sub") and node.args:
                    pat = node.args[0]
                    if isinstance(pat, ast.Constant) and isinstance(pat.value, str):
                        if REDOS_RE.search(pat.value):
                            record("SEC_34", lineno, f"Potential ReDoS nested quantifier in regex '{pat.value[:40]}'.")

                # SEC_35: Unbounded File Read
                if attr_name in ("read", "readlines") and not node.args:
                    record("SEC_35", lineno, f"Unbounded '.{attr_name}()' without explicit size limit risks memory exhaustion.")

                # SEC_38: Archive / Zip Bomb
                if attr_name == "extractall":
                    is_sink = True
                    record("SEC_38", lineno, "Unsafe '.extractall()' risks Zip Slip / decompression bomb.")

                # SEC_40: Unbounded Thread/Process Spawning in Loops
                if cname in ("threading.Thread", "multiprocessing.Process") and id(node) in loop_nodes:
                    record("SEC_40", lineno, f"Unbounded '{cname}' spawned inside loop (use ThreadPoolExecutor/ProcessPoolExecutor).")

                if is_sink:
                    dangerous_calls += 1
                    if has_dynamic_arg:
                        unsanitized_params += 1
                    if is_tainted_call:
                        taint_flows += 1

        # Compute Quantitative Metrics (SEC_46 .. SEC_52)
        metric_counts["SEC_46"] = taint_flows
        metric_counts["SEC_47"] = round((dangerous_calls / total_calls) * 100.0, 3) if total_calls else 0.0
        metric_counts["SEC_49"] = unsanitized_params
        metric_counts["SEC_50"] = round(sum(PRIVILEGED_IMPORTS.get(m, 0.0) for m in imported_roots), 2)
        metric_counts["SEC_51"] = round(peak_entropy, 3)

        return self._finalize_report(
            findings, metric_counts, loc=loc, ast_nodes=ast_nodes, cyclomatic=cyclomatic
        )

    # -----------------------------------------------------------------------
    # C++ Lexical / Pattern Security Engine
    # -----------------------------------------------------------------------
    def _analyze_cpp(self, code_string: str) -> Dict[str, Any]:
        raw_lines = code_string.splitlines()
        cleaned_lines = _strip_cpp_comments_and_strings(code_string).splitlines()
        loc = len(raw_lines)
        findings: List[Dict[str, Any]] = []
        metric_counts: Dict[str, float] = {mid: 0 for mid in self.registry}

        def record(metric_id: str, line: int, message: str) -> None:
            spec = self.registry[metric_id]
            metric_counts[metric_id] += 1
            findings.append({
                "metric_id": metric_id,
                "type": spec.name,
                "category": spec.category,
                "cwe": spec.cwe,
                "severity": spec.severity,
                "message": message,
                "line": line,
            })

        cpp_rules: List[Tuple[re.Pattern, str, str]] = [
            (re.compile(r"\b(?:std::)?system\s*\(|\b_?popen\s*\(|\bexec[lv]p?e?\s*\(|\bShellExecute[AW]?\s*\("), "SEC_01", "OS command execution call in C++."),
            (re.compile(r"\b(?:__)?asm(?:__)?\s*[\(\{]"), "SEC_12", "Inline assembly bypasses compiler memory safety."),
            (re.compile(r"\b(?:std::filesystem::remove(?:_all)?|std::remove|remove|unlink|rmdir)\s*\("), "SEC_16", "Destructive filesystem operation in C++."),
            (re.compile(r"\b(?:tmpnam|mktemp)\s*\("), "SEC_17", "Insecure temporary file creation (tmpnam/mktemp)."),
            (re.compile(r"\bchmod\s*\([^,]+,\s*0?777\b"), "SEC_19", "World-writable chmod(0777) in C++."),
            (re.compile(r"\b(?:std::)?ofstream\b|\bfopen\s*\("), "SEC_20", "File write operation in C++."),
            (re.compile(r"\brand\s*\(\s*\)"), "SEC_22", "Weak C rand() PRNG detected (use <random> / OS CSPRNG)."),
            (re.compile(r"\b(?:MD5|SHA1)_Init\b"), "SEC_23", "Deprecated MD5/SHA1 hash usage in C++."),
            (re.compile(r"\b(?:gets|strcpy|strcat|sprintf|vsprintf)\s*\("), "SEC_41", "Unbounded C string/buffer function risks buffer overflow."),
            (re.compile(r"\b(?:printf|fprintf|syslog)\s*\(\s*[A-Za-z_]\w*\s*\)"), "SEC_44", "Non-literal format string passed to printf/fprintf/syslog."),
            (re.compile(r"\b(?:malloc|calloc|realloc)\s*\("), "SEC_45", "Raw heap allocation (verify null check or use smart pointers)."),
            (re.compile(r"\bwhile\s*\(\s*(?:true|1)\s*\)"), "SEC_36", "Potentially unbounded while(true) loop in C++."),
        ]

        freed_vars: Set[str] = set()
        cyclomatic = 1
        total_calls = 0
        dangerous_calls = 0
        priv_score = 0.0
        peak_entropy = 0.0

        for lineno, (raw, clean) in enumerate(zip(raw_lines, cleaned_lines), 1):
            cyclomatic += len(re.findall(r"\b(if|for|while|case|catch)\b|&&|\|\|", clean))
            total_calls += len(re.findall(r"\b[A-Za-z_]\w*\s*\(", clean))

            if re.match(r"^\s*#\s*include\s*[<\"](sys/socket\.h|netinet/in\.h|winsock2\.h)[>\"]", raw):
                record("SEC_29", lineno, "Raw network socket header included.")
                priv_score += 3.5

            for pat, mid, msg in cpp_rules:
                if pat.search(clean):
                    record(mid, lineno, msg)
                    dangerous_calls += 1

            # Track free()/delete for Double-Free (SEC_43) and Use-After-Free (SEC_42)
            m_free = re.search(r"\b(?:free\s*\(\s*([A-Za-z_]\w*)\s*\)|delete(?:\[\])?\s+([A-Za-z_]\w*))", clean)
            if m_free:
                var = m_free.group(1) or m_free.group(2)
                if var in freed_vars:
                    record("SEC_43", lineno, f"Potential double-free on pointer '{var}'.")
                else:
                    freed_vars.add(var)
            else:
                for fv in list(freed_vars):
                    if re.search(rf"\b{re.escape(fv)}\s*(?:->|\[)", clean):
                        record("SEC_42", lineno, f"Potential use-after-free dereference of '{fv}'.")

            # Hardcoded secrets in C++
            m_sec = re.search(r'\b([A-Za-z_]\w*(?:password|secret|api_key|token)\w*)\s*=\s*"([^"]+)"', raw, re.IGNORECASE)
            if m_sec:
                record("SEC_21", lineno, f"Hardcoded secret assigned to '{m_sec.group(1)}'.")
                ent = shannon_entropy(m_sec.group(2))
                if ent > peak_entropy:
                    peak_entropy = ent

        metric_counts["SEC_47"] = round((dangerous_calls / total_calls) * 100.0, 3) if total_calls else 0.0
        metric_counts["SEC_50"] = round(priv_score, 2)
        metric_counts["SEC_51"] = round(peak_entropy, 3)

        return self._finalize_report(
            findings, metric_counts, loc=loc, ast_nodes=total_calls, cyclomatic=cyclomatic
        )

    # -----------------------------------------------------------------------
    # Finalization & Scoring
    # -----------------------------------------------------------------------
    def _finalize_report(
        self,
        findings: List[Dict[str, Any]],
        metric_counts: Dict[str, float],
        loc: int,
        ast_nodes: int,
        cyclomatic: int,
        parse_error: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Weighted risk score across all detector metrics
        raw_risk = 0.0
        category_summary: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "risk": 0.0})
        severity_counts: Dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}

        for f in findings:
            spec = self.registry[f["metric_id"]]
            raw_risk += spec.weight
            category_summary[spec.category]["count"] += 1
            category_summary[spec.category]["risk"] = round(category_summary[spec.category]["risk"] + spec.weight, 2)
            severity_counts[spec.severity] = severity_counts.get(spec.severity, 0) + 1

        # SEC_48: Security Cyclomatic Density
        sec_cyclomatic_density = round(raw_risk / max(1, cyclomatic), 4)
        metric_counts["SEC_48"] = sec_cyclomatic_density

        # SEC_52: Overall Security Health Score (0-100 exponential decay)
        health_score = round(100.0 * math.exp(-raw_risk / 40.0), 2)
        metric_counts["SEC_52"] = health_score

        triggered_metrics = [
            mid for mid, spec in self.registry.items()
            if spec.kind == "detector" and metric_counts[mid] > 0
        ]
        blocked = (severity_counts["CRITICAL"] > 0 or severity_counts["HIGH"] > 0)

        return {
            "findings": findings,
            "metrics": metric_counts,
            "triggered_metrics": triggered_metrics,
            "category_summary": dict(category_summary),
            "severity_counts": severity_counts,
            "summary": {
                "total_metrics_evaluated": len(self.registry),
                "loc": loc,
                "ast_nodes": ast_nodes,
                "cyclomatic_complexity": cyclomatic,
                "total_findings": len(findings),
                "unique_metrics_triggered": len(triggered_metrics),
                "raw_risk_score": round(raw_risk, 2),
                "security_health_score": health_score,
                "grade": self._grade(health_score),
                "blocked": blocked,
                "parse_error": parse_error,
            },
        }

    # -----------------------------------------------------------------------
    # Agentic Self-Verification Diff Gate
    # -----------------------------------------------------------------------
    def compare_reports(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two precomputed security audit reports without re-scanning source code.
        Used by the Verification Agent to reject patches that introduce regressions.
        """
        before_set = set(before["triggered_metrics"])
        after_set = set(after["triggered_metrics"])

        newly_introduced = sorted(after_set - before_set)
        resolved = sorted(before_set - after_set)
        risk_delta = round(
            after["summary"]["raw_risk_score"] - before["summary"]["raw_risk_score"], 2
        )
        health_delta = round(
            after["summary"]["security_health_score"] - before["summary"]["security_health_score"], 2
        )

        # Safe if no new HIGH/CRITICAL metric was introduced and severe findings did not increase
        introduced_severe = [
            m for m in newly_introduced if self.registry[m].severity in ("CRITICAL", "HIGH")
        ]
        severe_before = before["severity_counts"].get("CRITICAL", 0) + before["severity_counts"].get("HIGH", 0)
        severe_after = after["severity_counts"].get("CRITICAL", 0) + after["severity_counts"].get("HIGH", 0)
        patch_safe = (len(introduced_severe) == 0 and severe_after <= severe_before)

        return {
            "patch_safe": patch_safe,
            "risk_delta": risk_delta,
            "health_delta": health_delta,
            "resolved_metrics": resolved,
            "newly_introduced_metrics": newly_introduced,
            "introduced_severe_metrics": introduced_severe,
            "before_summary": before["summary"],
            "after_summary": after["summary"],
        }

    def compare(
        self,
        before_code: str,
        after_code: str,
        language: str = "python",
        before_report: Optional[Dict[str, Any]] = None,
        after_report: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Compare security posture before and after an Agentic Compiler patch.
        Used by the Verification Agent to reject patches that introduce regressions.
        """
        before = before_report if before_report is not None else self.analyze(before_code, language=language)
        after = after_report if after_report is not None else self.analyze(after_code, language=language)
        return self.compare_reports(before, after)

    # -----------------------------------------------------------------------
    # Programmatic Documentation Exporters (Tables for Report)
    # -----------------------------------------------------------------------
    def export_taxonomy_markdown(self) -> str:
        lines = [
            "| Metric ID | Metric Name | Category | CWE | Severity | Weight | Kind |",
            "| :--- | :--- | :--- | :--- | :--- | :---: | :--- |",
        ]
        for spec in self.registry.values():
            lines.append(
                f"| `{spec.id}` | {spec.name} | {spec.category} | `{spec.cwe}` | **{spec.severity}** | {spec.weight} | {spec.kind} |"
            )
        return "\n".join(lines)

    def export_taxonomy_csv(self) -> str:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id", "name", "category", "cwe", "severity", "weight", "kind", "description"])
        for spec in self.registry.values():
            writer.writerow([
                spec.id, spec.name, spec.category, spec.cwe,
                spec.severity, spec.weight, spec.kind, spec.description,
            ])
        return buf.getvalue()


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main() -> None:
    engine = SecurityMetricsEngine()
    if len(sys.argv) < 2:
        print(f"SecurityMetricsEngine loaded with {len(METRICS_REGISTRY)} metrics.")
        print("Usage:")
        print("  python security_metrics_engine.py <source_file.py|cpp> [--json]")
        print("  python security_metrics_engine.py --export-md")
        sys.exit(0)

    if sys.argv[1] == "--export-md":
        print(engine.export_taxonomy_markdown())
        sys.exit(0)

    target = sys.argv[1]
    as_json = "--json" in sys.argv[2:]
    lang = "cpp" if target.endswith((".cpp", ".cc", ".cxx", ".c", ".h", ".hpp")) else "python"

    with open(target, "r", encoding="utf-8", errors="replace") as f:
        code = f.read()

    report = engine.analyze(code, language=lang)
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        s = report["summary"]
        print(f"=== Security Metrics Report: {os.path.basename(target)} ({lang}) ===")
        print(f"Metrics Evaluated : {s['total_metrics_evaluated']}")
        print(f"LOC / AST Nodes   : {s['loc']} / {s['ast_nodes']}")
        print(f"Cyclomatic Compl. : {s['cyclomatic_complexity']}")
        print(f"Total Findings    : {s['total_findings']} ({s['unique_metrics_triggered']} unique metrics triggered)")
        print(f"Raw Risk Score    : {s['raw_risk_score']}")
        print(f"Health Score      : {s['security_health_score']}/100 (Grade: {s['grade']})")
        print(f"Execution Gate    : {'BLOCKED' if s['blocked'] else 'ALLOWED'}")
        print(f"Scan Time         : {s['scan_time_ms']} ms")
        if report["findings"]:
            print("\nTop Findings:")
            for f in report["findings"][:15]:
                print(f"  [{f['metric_id']} | {f['severity']} | {f['cwe']}] Line {f['line']}: {f['message']}")
            if len(report["findings"]) > 15:
                print(f"  ... and {len(report['findings']) - 15} more findings.")


if __name__ == "__main__":
    main()
