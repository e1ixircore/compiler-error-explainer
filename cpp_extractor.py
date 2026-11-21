# cpp_extractor.py - C++ counterpart of error_extractor.py.
# Runs the system C++ compiler with -fsyntax-only (for compile-check diagnostics),
# parses its diagnostics, and classifies each error into a clean set of error types
# that cpp_explainer.py knows how to explain and patch.
# Also provides run_cpp_code() for sandboxed compile + execution when the user presses Run.
#
# Supports GCC-style and Clang-style messages (on macOS `g++` is Apple clang).
import difflib
import functools
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from sandbox import run_sandboxed_command

CPP_EXTENSIONS = (".cpp", ".cc", ".cxx")
COMPILE_TIMEOUT = 15          # seconds, hard limit for one compiler invocation
_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_DIAG = re.compile(r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+): "
                   r"(?P<sev>fatal error|error|warning|note): (?P<msg>.*)$")
_Q = "[\u2018\u2019']"        # compilers may print ASCII or curly quotes

# Standard C++17 symbols -> header that defines them (crucial on Apple Clang, which often
# reports `use of undeclared identifier 'std'` or `'cout'` without printing a header hint).
STD_SYMBOL_HEADERS = {
    # <iostream>
    "cout": "iostream", "cin": "iostream", "cerr": "iostream", "clog": "iostream",
    "endl": "iostream", "flush": "iostream", "ws": "iostream",
    # <iomanip>
    "setw": "iomanip", "setprecision": "iomanip", "fixed": "iomanip", "setfill": "iomanip",
    # <string>
    "string": "string", "wstring": "string", "u16string": "string", "u32string": "string",
    "getline": "string", "to_string": "string", "stoi": "string", "stol": "string",
    "stoll": "string", "stof": "string", "stod": "string",
    # <string_view>
    "string_view": "string_view",
    # <vector>
    "vector": "vector",
    # <array>
    "array": "array",
    # <deque>, <list>, <queue>, <stack>
    "deque": "deque", "list": "list", "queue": "queue", "priority_queue": "queue", "stack": "stack",
    # <map>, <unordered_map>, <set>, <unordered_set>
    "map": "map", "multimap": "map",
    "unordered_map": "unordered_map", "unordered_multimap": "unordered_map",
    "set": "set", "multiset": "set",
    "unordered_set": "unordered_set", "unordered_multiset": "unordered_set",
    # <utility>, <tuple>
    "pair": "utility", "make_pair": "utility", "move": "utility", "forward": "utility", "swap": "utility",
    "tuple": "tuple", "make_tuple": "tuple", "tie": "tuple", "get": "tuple",
    # <algorithm>
    "sort": "algorithm", "stable_sort": "algorithm", "find": "algorithm", "find_if": "algorithm",
    "count": "algorithm", "count_if": "algorithm", "reverse": "algorithm", "min": "algorithm",
    "max": "algorithm", "minmax": "algorithm", "min_element": "algorithm", "max_element": "algorithm",
    "transform": "algorithm", "copy": "algorithm", "fill": "algorithm", "binary_search": "algorithm",
    "lower_bound": "algorithm", "upper_bound": "algorithm", "unique": "algorithm", "clamp": "algorithm",
    # <numeric>
    "accumulate": "numeric", "iota": "numeric", "gcd": "numeric", "lcm": "numeric",
    # <cmath>
    "sqrt": "cmath", "pow": "cmath", "abs": "cmath", "fabs": "cmath", "floor": "cmath",
    "ceil": "cmath", "round": "cmath", "sin": "cmath", "cos": "cmath", "tan": "cmath",
    "log": "cmath", "log10": "cmath", "exp": "cmath", "fmod": "cmath",
    # <cstdio>, <cstdlib>, <cstring>
    "printf": "cstdio", "scanf": "cstdio", "snprintf": "cstdio", "fprintf": "cstdio", "puts": "cstdio",
    "malloc": "cstdlib", "calloc": "cstdlib", "free": "cstdlib", "exit": "cstdlib",
    "atoi": "cstdlib", "atof": "cstdlib", "rand": "cstdlib", "srand": "cstdlib",
    "strlen": "cstring", "strcmp": "cstring", "strncmp": "cstring", "memcpy": "cstring", "memset": "cstring",
    # <fstream>, <sstream>
    "ifstream": "fstream", "ofstream": "fstream", "fstream": "fstream",
    "stringstream": "sstream", "istringstream": "sstream", "ostringstream": "sstream",
    # <memory>, <functional>, <limits>, <stdexcept>, <optional>, <variant>
    "unique_ptr": "memory", "shared_ptr": "memory", "weak_ptr": "memory",
    "make_unique": "memory", "make_shared": "memory",
    "function": "functional", "bind": "functional",
    "numeric_limits": "limits",
    "runtime_error": "stdexcept", "logic_error": "stdexcept", "out_of_range": "stdexcept",
    "invalid_argument": "stdexcept", "exception": "exception",
    "optional": "optional", "nullopt": "optional", "variant": "variant",
    "assert": "cassert",
}

ALL_STD_HEADERS = sorted(set(STD_SYMBOL_HEADERS.values()) | {
    "bitset", "cctype", "chrono", "climits", "cstddef", "cstdint", "ctime",
    "filesystem", "initializer_list", "iterator", "mutex", "random", "regex",
    "thread", "type_traits",
})

# High-value compiler warnings that represent real defects (promoted to actionable errors).
_PROMOTED_WARNING_TYPES = {
    "DivisionByZero",
    "ArrayOutOfBounds",
    "MissingReturn",
    "AssignmentInCondition",
    "UninitializedVariable",
}


class CompilerNotFound(RuntimeError):
    pass


def is_cpp_name(name):
    return bool(name) and str(name).lower().endswith(CPP_EXTENSIONS)


def included_headers(code):
    return set(re.findall(r"^\s*#\s*include\s*<([^>]+)>", code, re.MULTILINE))


# ----------------------------------------------------------------------
# Compiler discovery
# ----------------------------------------------------------------------
@functools.lru_cache(maxsize=1)
def find_compiler():
    for cand in ("g++", "clang++"):
        path = shutil.which(cand)
        if path:
            return path
    return None


@functools.lru_cache(maxsize=1)
def compiler_flavor():
    cc = find_compiler()
    if not cc:
        return "none"
    try:
        out = subprocess.run([cc, "--version"], capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return "unknown"
    return "clang" if "clang" in out.lower() else "gcc"


@functools.lru_cache(maxsize=1)
def _flags():
    cc = find_compiler()
    flags = ["-fsyntax-only", "-Wall", "-Wextra", "-std=c++17"]
    if compiler_flavor() == "gcc":
        # gcc>=11 expands tabs in reported columns by default; ask for byte columns.
        probe = [cc, "-fdiagnostics-column-unit=byte", "-fsyntax-only", "-x", "c++", "-"]
        try:
            if subprocess.run(probe, input="", capture_output=True, text=True, timeout=10).returncode == 0:
                flags.append("-fdiagnostics-column-unit=byte")
        except Exception:
            pass
    return flags


def compiler_label():
    cc = find_compiler()
    return f"{os.path.basename(cc)} ({compiler_flavor()})" if cc else "none"


# ----------------------------------------------------------------------
# Running + parsing
# ----------------------------------------------------------------------
def _run(workdir, filename, extra_flags=None, output_bin=None):
    cc = find_compiler()
    if not cc:
        raise CompilerNotFound("No C++ compiler found. Install g++ or clang++ and make sure it is on PATH.")
    if output_bin:
        cmd = [cc, "-std=c++17", "-O0", "-Wall", *(extra_flags or []), filename, "-o", output_bin]
    else:
        cmd = [cc, *_flags(), *(extra_flags or []), filename]
    if os.name == "posix" and shutil.which("sh"):
        # CPU/memory ceilings for the compiler itself (template bombs, giant constexpr loops).
        # Failures of `ulimit` are ignored (e.g. macOS refuses -v).
        cmd = ["sh", "-c", 'ulimit -t 10 2>/dev/null; ulimit -v 4000000 2>/dev/null; exec "$@"', "sh"] + cmd
    env = dict(os.environ, LC_ALL="C", LANG="C", LANGUAGE="C")   # force English messages
    return subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, errors="replace",
                          timeout=COMPILE_TIMEOUT, env=env, stdin=subprocess.DEVNULL,
                          start_new_session=True)


def _parse(stderr, filename, code=""):
    diags, cur = [], None
    lines = code.split("\n")
    included = included_headers(code)
    for raw in _ANSI.sub("", stderr).splitlines():
        m = _DIAG.match(raw)
        if not m or os.path.basename(m["file"]) != filename:
            continue                      # source/caret lines, or diagnostics inside system headers
        sev = "error" if m["sev"] in ("error", "fatal error") else m["sev"]
        if sev == "note":
            if cur is not None:
                cur["notes"].append(m["msg"])
            continue
        cur = {"severity": sev, "line": int(m["line"]), "column": int(m["col"]),
               "message": m["msg"], "notes": [], "fatal": m["sev"] == "fatal error"}
        diags.append(cur)
    for d in diags:
        _classify(d, lines, included)
    return diags


def cpp_check(code):
    """Compile-check `code`. Returns {errors, warnings, compile_ms, compiler, timed_out}."""
    t0 = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="intellifix_cpp_") as tmp:
        fname = "input.cpp"
        with open(os.path.join(tmp, fname), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(code)
        try:
            done = _run(tmp, fname)
        except subprocess.TimeoutExpired:
            d = {"severity": "error", "line": 1, "column": 1, "notes": [], "fatal": True,
                 "message": f"Compilation exceeded the {COMPILE_TIMEOUT}-second time limit.",
                 "error_type": "CompileTimeout", "name": None, "header": None, "suggestion": None}
            return {"errors": [d], "warnings": [], "compiler": compiler_label(),
                    "compile_ms": (time.perf_counter() - t0) * 1000, "timed_out": True}
    diags = _parse(done.stderr, fname, code)
    errors = []
    warnings = []
    for d in diags:
        if d["severity"] == "error" or d["error_type"] in _PROMOTED_WARNING_TYPES:
            errors.append(d)
        else:
            warnings.append(d)
    if done.returncode != 0 and not errors:
        # Compiler failed without a parsable diagnostic (bad install, linker-ish message, ...).
        tail = (done.stderr.strip().splitlines() or ["unknown compiler failure"])[-1]
        errors = [{"severity": "error", "line": 1, "column": 1, "message": tail, "notes": [],
                   "fatal": True, "error_type": "CompileError", "name": None, "header": None,
                   "suggestion": None}]
    return {"errors": errors, "warnings": warnings,
            "compiler": compiler_label(), "compile_ms": (time.perf_counter() - t0) * 1000,
            "timed_out": False}


def run_cpp_code(code, timeout=5):
    """Compile and execute C++ code in an isolated temp directory with hard timeouts."""
    t0 = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="intellifix_cpp_run_") as tmp:
        fname = "input.cpp"
        out_bin = os.path.join(tmp, "prog")
        with open(os.path.join(tmp, fname), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(code)
        try:
            comp = _run(tmp, fname, output_bin=out_bin)
        except subprocess.TimeoutExpired:
            return {
                "error_type": "CompileTimeout",
                "error_message": f"Compilation exceeded the {COMPILE_TIMEOUT}-second time limit.",
                "line_number": None,
                "traceback": "",
                "stdout": "",
                "execution_time_sec": time.perf_counter() - t0,
            }
        if comp.returncode != 0:
            diags = _parse(comp.stderr, fname, code)
            errs = [d for d in diags if d["severity"] == "error"]
            msg = "\n".join(f"line {e['line']}: {e['message']}" for e in errs[:5]) or comp.stderr.strip()
            return {
                "error_type": errs[0]["error_type"] if errs else "CompileError",
                "error_message": msg,
                "line_number": errs[0]["line"] if errs else 1,
                "traceback": comp.stderr,
                "stdout": "",
                "execution_time_sec": time.perf_counter() - t0,
            }
        try:
            run_start = time.perf_counter()
            proc = run_sandboxed_command(
                [out_bin],
                cwd=tmp,
                timeout=timeout,
                allowed_executables=[out_bin],
            )
            elapsed = time.perf_counter() - run_start
        except subprocess.TimeoutExpired as error:
            partial = error.stdout or ""
            if isinstance(partial, bytes):
                partial = partial.decode("utf-8", errors="replace")
            return {
                "error_type": "TimeoutError",
                "error_message": f"Execution exceeded the {timeout}-second time limit.",
                "line_number": None,
                "traceback": "",
                "stdout": partial,
                "execution_time_sec": timeout,
            }
        if proc.returncode != 0:
            sig_names = {
                -signal.SIGFPE: ("ZeroDivisionError", "Floating point exception / division by zero (SIGFPE)."),
                -signal.SIGSEGV: ("SegmentationFault", "Invalid memory access / out-of-bounds pointer or array (SIGSEGV)."),
                -signal.SIGABRT: ("RuntimeError", proc.stderr.strip() or "Program aborted (SIGABRT)."),
                -signal.SIGBUS: ("BusError", "Invalid memory alignment/address (SIGBUS)."),
            }
            etype, emsg = sig_names.get(
                proc.returncode,
                ("RuntimeError", proc.stderr.strip() or f"Program exited with status {proc.returncode}."),
            )
            return {
                "error_type": etype,
                "error_message": emsg,
                "line_number": None,
                "traceback": proc.stderr,
                "stdout": proc.stdout,
                "execution_time_sec": elapsed,
            }
        out = proc.stdout
        if proc.stderr.strip():
            out = (out + "\n" if out else "") + proc.stderr
        return {
            "error_type": None,
            "error_message": None,
            "line_number": None,
            "traceback": None,
            "stdout": out,
            "execution_time_sec": elapsed,
        }


# ----------------------------------------------------------------------
# Classification: diagnostic text -> error type the explainer understands
# ----------------------------------------------------------------------
def _first_quoted(text):
    m = re.search(_Q + r"([^\u2018\u2019']+)" + _Q, text or "")
    return m.group(1) if m else None


def _std_symbol_after_col(line, col):
    """If the source around (col) is `std::foo`, return `'foo'`."""
    if not line:
        return None
    idx = max(0, (col or 1) - 1)
    m = re.match(r"std\s*::\s*([A-Za-z_]\w*)", line[idx:])
    if m:
        return m.group(1)
    # Fallback: search anywhere on the line for std::<sym>
    m2 = re.search(r"\bstd\s*::\s*([A-Za-z_]\w*)", line)
    return m2.group(1) if m2 else None


def _all_quoted(text):
    return re.findall(_Q + r"([^\u2018\u2019']+)" + _Q, text or "")


def _classify(d, lines=None, included=None):
    msg = d["message"]
    blob = " | ".join([msg] + d["notes"])
    quoted = _all_quoted(msg)
    name = quoted[0] if quoted else None
    included = included or set()
    line_text = ""
    if lines and 1 <= d.get("line", 0) <= len(lines):
        line_text = lines[d["line"] - 1]

    header = None
    for pat in (r"defined in header " + _Q + r"<([^>]+)>", r"include the header <([^>]+)>",
                r"#include <([^>]+)>"):
        m = re.search(pat, blob)
        if m:
            header = m.group(1)
            break
    sm = re.search(r"did you mean " + _Q + r"([^\u2018\u2019']+)" + _Q, blob)
    suggestion = sm.group(1) if sm else None
    etype = "CompileError"
    expected_type = None
    actual_type = None

    # ---- High-value warning classifications (checked first so warnings classify accurately) ----
    if re.search(r"division by zero", msg, re.IGNORECASE):
        etype = "DivisionByZero"
    elif re.search(r"array index .+ is past the end|above array bounds|out of bounds", msg, re.IGNORECASE):
        etype = "ArrayOutOfBounds"
    elif re.search(r"non-void function (?:does not|'.+' should) return a value|control reaches end of non-void function", msg):
        etype = "MissingReturn"
    elif re.search(r"using the result of an assignment as a condition|suggest parentheses around assignment", msg):
        etype = "AssignmentInCondition"
    elif re.search(r"is uninitialized when used here|may be used uninitialized", msg):
        etype = "UninitializedVariable"

    # ---- Standard & Extended C++ compiler error classifications ----
    elif re.search(r"No such file or directory|file not found", msg):
        m = re.match(r"(.+?): No such file or directory", msg)
        name = m.group(1) if m else name
        etype = "MissingHeaderFile"
        if name and not suggestion:
            close = difflib.get_close_matches(name, ALL_STD_HEADERS, n=1, cutoff=0.7)
            if close:
                suggestion = close[0]
    elif re.search(r"'main' must return 'int'|::main.*must return 'int'", msg):
        etype = "InvalidMainSignature"
    elif re.search(r"expected ';' after (?:struct|class|enum|union)", msg):
        etype = "MissingClassSemicolon"
    elif re.search(r"is not a member of " + _Q + r"std" + _Q, msg) or \
            re.search(r"no (?:member|template) named " + _Q + r"[^\u2018\u2019']+" + _Q + r" in namespace " + _Q + r"std" + _Q, msg):
        etype = "MissingInclude"
        if not header and name in STD_SYMBOL_HEADERS:
            header = STD_SYMBOL_HEADERS[name]
    elif re.search(r"unknown type name|no template named|unknown template name|does not name a type", msg):
        # e.g. `unknown type name 'string'; did you mean 'std::string'?`
        # or   `no template named 'vector'; did you mean 'std::vector'?`
        if name in STD_SYMBOL_HEADERS:
            hdr = STD_SYMBOL_HEADERS[name]
            if hdr not in included:
                etype = "MissingInclude"
                header = hdr
            else:
                etype = "MissingStdPrefix"
                suggestion = suggestion or f"std::{name}"
        elif suggestion and suggestion.startswith("std::"):
            etype = "MissingStdPrefix"
        else:
            etype = "UnknownType"
            if name and not suggestion:
                candidates = list(STD_SYMBOL_HEADERS.keys()) + ["int", "double", "float", "bool", "char", "void", "size_t", "auto"]
                close = difflib.get_close_matches(name, candidates, n=1, cutoff=0.72)
                if close:
                    suggestion = f"std::{close[0]}" if close[0] in STD_SYMBOL_HEADERS else close[0]
    elif re.search(r"use of class template .+ requires template arguments|missing template arguments|deduction of template arguments", msg):
        etype = "MissingTemplateArgs"
    elif re.search(r"member reference type .+ is a pointer|which is of pointer type", msg):
        etype = "PointerMemberAccess"
    elif re.search(r"member reference type .+ is not a pointer|base operand of '->' has non-pointer type", msg):
        etype = "ValueMemberAccess"
    elif re.search(r"cannot assign to variable .+ with const-qualified type|assignment of read-only", msg):
        etype = "ConstModification"
    elif re.search(r"default initialization of an object of const type|uninitialized 'const", msg):
        etype = "ConstUninitialized"
    elif re.search(r"indirection requires pointer operand|invalid type argument of unary '\*'", msg):
        etype = "InvalidDereference"
        if quoted:
            actual_type = quoted[0]
    elif re.search(r"subscripted value is not an array, pointer, or vector|invalid types .+ for array subscript", msg):
        etype = "InvalidSubscript"
    elif re.search(r"called object type .+ is not a function|cannot be used as a function", msg):
        etype = "NotCallable"
        if quoted:
            actual_type = quoted[0]
    elif re.search(r"too (?:few|many) arguments to function call|too (?:few|many) arguments to function", msg):
        etype = "WrongArgumentCount"
    elif re.search(r"void function .+ should not return a value|return-statement with a value, in function returning 'void'", msg):
        etype = "VoidReturnValue"
    elif re.search(r"(?:break|continue) statement not in loop", msg):
        etype = "MisplacedLoopControl"
    elif re.search(r"expression is not assignable|lvalue required as left operand", msg):
        etype = "NotAssignable"
    elif re.search(r"implicit instantiation of undefined template|incomplete type", msg):
        # Often caused by missing <sstream> or <fstream> or <string>
        for sym, hdr in (("ifstream", "fstream"), ("ofstream", "fstream"), ("fstream", "fstream"),
                         ("stringstream", "sstream"), ("istringstream", "sstream"), ("ostringstream", "sstream"),
                         ("basic_string", "string"), ("vector", "vector"), ("array", "array")):
            if sym in msg and hdr not in included:
                etype = "MissingInclude"
                name = sym
                header = hdr
                break
        else:
            etype = "IncompleteType"
    elif re.search(r"non-const lvalue reference to type .+ cannot bind to|cannot bind non-const lvalue reference", msg):
        etype = "ReferenceBinding"
        if len(quoted) >= 2:
            expected_type, actual_type = quoted[0], quoted[1]
    elif re.search(r"duplicate case value", msg):
        etype = "DuplicateCase"
    elif re.search(r"was not declared in this scope|use of undeclared identifier", msg):
        # Apple Clang reports `use of undeclared identifier 'std'` when no std header is included at all!
        if name == "std":
            sym = _std_symbol_after_col(line_text, d.get("column"))
            if sym and sym in STD_SYMBOL_HEADERS and STD_SYMBOL_HEADERS[sym] not in included:
                etype = "MissingInclude"
                name = sym
                header = STD_SYMBOL_HEADERS[sym]
            else:
                etype = "MissingInclude"
                header = header or "iostream"
        elif suggestion and suggestion.startswith("std::"):
            etype = "MissingStdPrefix"
        elif name in STD_SYMBOL_HEADERS:
            hdr = STD_SYMBOL_HEADERS[name]
            if hdr not in included:
                etype = "MissingInclude"
                header = hdr
            else:
                etype = "MissingStdPrefix"
                suggestion = f"std::{name}"
        elif header and not suggestion:
            etype = "MissingInclude"
        else:
            etype = "UndeclaredIdentifier"
    elif re.match(r"expected (?:" + _Q + r"," + _Q + r" or )?" + _Q + r";" + _Q, msg) \
            and not re.search(r"before " + _Q + r"\{", msg):
        etype = "MissingSemicolon"
    elif re.search(r"expected " + _Q + r"\}" + _Q + r" at end of input", msg) or re.fullmatch(r"expected " + _Q + r"\}" + _Q, msg):
        etype = "MissingBrace"
    elif re.search(r"extraneous closing brace|expected declaration before " + _Q + r"\}", msg):
        etype = "ExtraBrace"
    elif re.search(r"expected " + _Q + r"\)" + _Q, msg):
        etype = "MissingParen"
    elif re.search(r"invalid operands to binary", msg) and (
            re.search(r"ostream|istream", msg)
            or re.search(r"\b(?:cout|cerr|clog)\b.*>>|\bcin\b.*<<", line_text)):
        etype = "WrongStreamOperator"
    elif re.search(r"invalid conversion from|cannot convert|cannot initialize|no viable conversion|"
                   r"invalid operands to binary|incompatible|assigning to .+ from incompatible type|"
                   r"no viable overloaded '='", msg):
        etype = "TypeMismatch"
        if len(quoted) >= 2:
            expected_type, actual_type = quoted[0], quoted[1]
    elif re.search(r"no matching function for call|no matching member function|no viable function|"
                   r"no matching constructor", msg):
        etype = "NoMatchingFunction"
    elif re.search(r"has no member named|no member named", msg):
        etype = "NoSuchMember"
    elif re.search(r"redefinition of|redeclaration of|conflicting declaration", msg):
        etype = "Redefinition"
    elif re.search(r"expected (?:unqualified-id|primary-expression|declaration|expression|identifier)", msg):
        etype = "SyntaxError"
    d.update(
        error_type=etype,
        name=name,
        header=header,
        suggestion=suggestion,
        expected_type=expected_type,
        actual_type=actual_type,
    )


# ----------------------------------------------------------------------
# IR (same spirit as ir_generator.py, minus the Python AST fields)
# ----------------------------------------------------------------------
def diag_to_ir(d, code, compiler=None):
    lines = code.split("\n")
    ln = d.get("line")
    snippet = lines[ln - 1].strip() if ln and 1 <= ln <= len(lines) else None
    return {
        "error_type": d["error_type"], "error_message": d["message"], "line_number": ln,
        "column": d.get("column"), "error_variable": d.get("name"), "name": d.get("name"),
        "header": d.get("header"), "suggestion": d.get("suggestion"), "notes": d.get("notes", []),
        "expected_type": d.get("expected_type"), "actual_type": d.get("actual_type"),
        "phase": "compiler", "language": "cpp", "compiler": compiler, "snippet": snippet,
        "error_category": "compiler",
        "traceback": "(compiler diagnostics: code was not executed)",
    }


def extract_cpp_error(code):
    """Mirror of extract_error(): IR dict for the FIRST error, plus every error found."""
    res = cpp_check(code)
    ir = {"error_type": None, "error_message": None, "line_number": None, "traceback": None,
          "stdout": "", "compiler": res["compiler"],
          "green_metrics": {"execution_time_sec": res["compile_ms"] / 1000,
                            "emissions_kg": 0, "energy_consumed_kwh": 0}}
    if res["errors"]:
        ir.update(diag_to_ir(res["errors"][0], code, res["compiler"]))
        ir["all_errors"] = [diag_to_ir(e, code, res["compiler"]) for e in res["errors"]]
    ir["warnings"] = res["warnings"]
    return ir
