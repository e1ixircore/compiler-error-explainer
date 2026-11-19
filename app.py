from collections import Counter
import difflib
import threading
import glob
import json
import os
import time
import re

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from error_extractor import extract_error, run_code   # run_code = your sandbox
from nlp_explainer import NLPExplainer
from ir_generator import IRGenerator
from security_analyzer import SecurityAnalyzer
from static_analyzer import static_check
from cpp_explainer import (
    apply_fix as apply_cpp_fix,
    explain as explain_cpp_error,
    hides_crash as cpp_hides_crash,
    meaning as cpp_meaning,
)
from cpp_extractor import (
    CPP_EXTENSIONS,
    CompilerNotFound,
    extract_cpp_error,
    is_cpp_name,
    run_cpp_code,
)

# CRITICAL/HIGH findings mean "do not execute, do not save".
BLOCKING = {"CRITICAL", "HIGH"}
MAX_REPAIR_PASSES = 100    # hard cap on patch passes (each pass fixes ONE error)
MAX_REPAIR_SECONDS = 60    # wall-clock budget: every runtime pass spawns a sandbox, so bound the total
MAX_CODE_BYTES = 100_000   # reject giant inputs before parsing (protects the compiler itself)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
class CompilerError:
    def __init__(self, error_type, message, line_number, category, traceback_info):
        self.error_type = error_type
        self.message = message
        self.line_number = line_number
        self.category = category
        self.traceback_info = traceback_info


def _available_test_files():
    files = []
    for extension in (".py",) + CPP_EXTENSIONS:
        files.extend(glob.glob(f"test*{extension}"))
        files.extend(glob.glob(f"*_fixed{extension}"))
    all_files = sorted(set(files))
    all_files = [f for f in all_files
                 if f not in ["test_ir.py", "test_nlp.py", "sample_input.py", "sample_input_fixed.py"]]
    return [{"filename": f, "is_fixed": "_fixed." in f, "language": "cpp" if is_cpp_name(f) else "python"}
            for f in all_files]


def detect_language(filename=None, code="", explicit=None):
    """Decide whether source code is 'cpp' or 'python'."""
    if isinstance(explicit, str):
        val = explicit.strip().lower()
        if val in ("cpp", "c++", "cxx", "cc"):
            return "cpp"
        if val in ("py", "python"):
            return "python"
    if filename:
        if is_cpp_name(filename):
            return "cpp"
        if str(filename).lower().endswith(".py"):
            return "python"
    if isinstance(code, str) and code.strip():
        if re.search(r"^\s*#\s*include\s*[<\"].+[>\"]", code, re.MULTILINE):
            return "cpp"
        if re.search(r"\b(?:int|void)\s+main\s*\(", code) or re.search(r"\busing\s+namespace\s+std\b", code):
            return "cpp"
        if re.search(r"\bstd::\w+", code) or re.search(r"\b(?:cout|cerr)\s*<<|\bcin\s*>>", code):
            return "cpp"
    return "python"


def safe_name(name):
    """Single whitelist check used by every endpoint.
    A name is valid only if it is a bare filename (no path parts) that appears
    in the list /api/files shows. This blocks path traversal like ../../x."""
    if not name or os.path.basename(name) != name:
        return None
    return name if name in {i["filename"] for i in _available_test_files()} else None


def read_source(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(filename, "r", encoding="latin-1") as f:
            return f.read()


def scan(code, language="python"):
    """Returns (vulns, formatted log lines, is_blocked)."""
    vulns = SecurityAnalyzer().scan_code(code, language=language)
    log = [f"[{v['severity']}] Line {v['line']}: {v['message']}" for v in vulns]
    return vulns, log, any(v["severity"] in BLOCKING for v in vulns)


def fix_is_safe(original, fixed, language="python"):
    """A patch may never ADD a vulnerability class that the original didn't have."""
    sa = SecurityAnalyzer()
    before = Counter(v["type"] for v in sa.scan_code(original, language=language))
    after = Counter(v["type"] for v in sa.scan_code(fixed, language=language))
    return all(after[t] <= before[t] for t in after)

def verify_fix(original, fixed):
    """Closed-loop check: feed the patch back through the same pipeline.
    This measures whether the fix WORKS, not whether the text resembles a template."""
    if fixed == original:
        return {"verdict": "NO FIX GENERATED", "detail": "No auto-fix rule for this error; explanation only."}
    try:
        static_errs = static_check(fixed)          # stage 1: does it parse + pass symbol-table checks?
    except SyntaxError as e:
        return {"verdict": "REJECTED", "detail": f"Patch does not parse: {e.msg} (line {e.lineno})"}
    except (RecursionError, MemoryError):
        return {"verdict": "REJECTED", "detail": "Patch too deeply nested to analyze."}
    if static_errs:
        e = static_errs[0]
        return {"verdict": "PARTIAL",
                "detail": f"{len(static_errs)} static error(s) remain; first: {e['error_type']} on line {e['line_number']}"}
    if scan(fixed)[2]:                              # stage 2: patch must not be dangerous
        return {"verdict": "REJECTED", "detail": "Patch contains critical security findings."}
    try:
        r = run_code(fixed)                         # stage 3: does it actually run?
    except RuntimeError as e:
        return {"verdict": "REJECTED", "detail": f"Sandbox failure: {e}"}
    if r["error_type"]:
        return {"verdict": "PARTIAL",
                "detail": f"Runs, but still raises {r['error_type']}: {r['error_message']}"}
    return {"verdict": "VERIFIED", "detail": "Patched code passes static analysis, security scan, and sandboxed execution."}

def build_metrics(ir_dict):
    """Only real, measured values. Nothing random."""
    g = (ir_dict or {}).get("green_metrics") or {}
    t = g.get("execution_time_sec") or 0
    kg = g.get("emissions_kg") or 0
    kwh = g.get("energy_consumed_kwh") or 0
    return (f"Execution Time\n{t*1000:.2f} ms\n\n"
            f"CodeCarbon Emissions\n{kg*1e6:.6f} mg CO2 eq\n\n"
            f"Energy Consumed\n{kwh*1e6:.6f} mWh\n")


def build_metrics_data(scan_ms, ir_dict=None):
    """Structured metrics for the bottom summary bar in index.html."""
    import analytics_data
    power_w = analytics_data.load_power()["mean_w"]
    g = (ir_dict or {}).get("green_metrics") or {}
    run_ms = round((g.get("execution_time_sec") or 0) * 1000, 2)
    emissions_mg = round((g.get("emissions_kg") or 0) * 1e6, 4)
    return {
        "scan_ms": round(scan_ms, 2),
        "run_ms": run_ms,
        "est_energy_mj": round(power_w * scan_ms, 1),
        "power_w": power_w,
        "codecarbon": emissions_mg > 0,
        "emissions_mg": emissions_mg,
    }

def _changed_lines(before, after):
    """(sign, text) pairs for lines a patch removed ('-') or added ('+'), for display."""
    diff = list(difflib.unified_diff(before.split("\n"), after.split("\n"), lineterm="", n=0))
    return [(l[0], l[1:].strip()) for l in diff[2:] if not l.startswith("@@")]



# ----------------------------------------------------------------------
# LINE TRACKING
# The repair loop patches ONE error per pass, and some patches INSERT lines (the NameError
# fallback, the import guard). So an error found in pass 3 is reported against the PATCHED code.
# The UI highlights the ORIGINAL code, so we carry `origin`: origin[i] = the original line number
# of line i of the current code (None = a line the repair loop inserted).
# ----------------------------------------------------------------------
def _remap_origin(origin, before, after):
    """Update `origin` after a patch, using a line diff of before -> after."""
    a, b = before.split("\n"), after.split("\n")
    new = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            new += origin[i1:i2]                      # untouched lines keep their original number
        elif tag == "replace":
            old = origin[i1:i2]                       # 1 line -> 4 lines: first keeps the number
            new += [old[k] if k < len(old) else None for k in range(j2 - j1)]
        elif tag == "insert":
            new += [None] * (j2 - j1)                 # brand-new lines have no original line
        # "delete": those lines simply disappear
    return new


def _orig_line(origin, ln):
    """Patched-code line number -> original line number (nearest earlier original line if inserted)."""
    if not ln or not origin:
        return None
    i = min(ln, len(origin)) - 1
    while i >= 0 and origin[i] is None:
        i -= 1
    return origin[i] if i >= 0 else None


def repair_loop(code, max_iters=MAX_REPAIR_PASSES, time_budget=MAX_REPAIR_SECONDS, first_ir=None):
    """Agent loop: perceive (analyze) -> decide (pick rule) -> act (patch) -> observe (re-analyze).
    Runs UNTIL THE CODE IS CLEAN, one error per pass, so any number of errors can be fixed.
    If one static error has no safe automatic fix, it is recorded and skipped so remaining static
    errors in the same file are still reported and fixed.
    Termination is guaranteed by four independent stops:
      1. clean           : no error remains                       -> success
      2. no safe fix     : all remaining errors have no safe rule -> partial / stuck
      3. no progress     : patch reproduces an earlier program, or the same error recurs 3x
      4. budget          : pass cap or wall-clock limit reached   -> partial
    first_ir lets the caller hand over an analysis it already ran (avoids executing twice)."""
    history, current = [], code
    seen_states = {code}                 # every program version produced so far (cycle detection)
    repeats = Counter()                  # how often the same (type, message, line) came back
    skipped_static = set()               # unfixable static error keys (type, msg, orig_line)
    t_start = time.perf_counter()
    origin = list(range(1, len(code.split("\n")) + 1))   # line i of `current` came from original line origin[i]
    for i in range(max_iters):
        if time.perf_counter() - t_start > time_budget:
            history.append({"step": "final",
                            "result": f"stopped: {time_budget}s time budget reached; errors may remain"})
            break
        ir_dict = first_ir if (i == 0 and first_ir is not None) else extract_error(current)   # perceive
        if not ir_dict.get("error_type"):
            history.append({"step": i + 1, "result": "clean"})
            break
        tb = ir_dict.get("traceback") or ""
        stage = "static" if tb.startswith("(static") else "runtime"
        if ir_dict["error_type"] in ("SyntaxError", "IndentationError"):
            stage = "parser"             # rejected before any AST existed

        # If static analysis found multiple errors and earlier ones were unfixable, advance to
        # the next unskipped static error so EVERY error is explained and fixable ones are patched.
        active = ir_dict
        if stage == "static" and ir_dict.get("all_errors"):
            picked = None
            for cand in ir_dict["all_errors"]:
                key = (cand["error_type"], cand.get("error_message"), _orig_line(origin, cand.get("line_number")))
                if key not in skipped_static:
                    picked = cand
                    break
            if picked is None:
                break                    # every remaining static error was already reported as unfixable
            active = dict(ir_dict,
                          error_type=picked["error_type"],
                          error_message=picked.get("error_message"),
                          line_number=picked.get("line_number"),
                          column=picked.get("column"),
                          suggestion=picked.get("suggestion"))

        err = CompilerError(active["error_type"], active.get("error_message"),
                            active.get("line_number"), stage, tb)
        ir = json.loads(IRGenerator(current, err).generate_ir())   # the IR: one JSON payload PER error
        ir["suggestion"] = active.get("suggestion")           # symbol-table "did you mean"
        # Promised fields for the Diagnostic JSON (now attached to every issue, not just the first).
        ir["phase"] = stage                                   # "parser" | "static" | "runtime"
        ir["column"] = active.get("column")                   # only the static checker knows columns

        t0 = time.perf_counter()
        explanation = explainer.explain(ir)                   # explain THIS error
        explain_ms = (time.perf_counter() - t0) * 1000

        lines, ln = current.split("\n"), ir.get("line_number")
        src = lines[ln - 1].strip() if ln and ln <= len(lines) else ""
        ir["snippet"] = src or None
        # tb frames named "<string>": the FIRST is the sandbox runner's own exec()/compile() call
        # (infrastructure noise), so keep only frames that belong to the user's code.
        frames = []
        for l in tb.split("\n"):
            m = re.match(r'\s*File "<string>", line (\d+)(?:, in (.+))?', l)
            if m:
                frames.append(f"line {m.group(1)}" + (f" in {m.group(2)}" if m.group(2) else ""))
        frames = frames[1:]
        orig_ln = _orig_line(origin, ln)
        entry = {"step": i + 1, "error": ir["error_type"], "line": ln, "column": ir["column"],
                 "stage": stage, "source": src, "ir": ir, "trace": frames,
                 "explanation": explanation, "explain_ms": explain_ms, "patch": [],
                 "orig_line": orig_ln}      # where to highlight in the ORIGINAL code

        sig = (ir["error_type"], ir.get("error_message"), ln)
        static_key = (ir["error_type"], ir.get("error_message"), orig_ln)
        repeats[sig] += 1
        fixed = explainer.generate_fixed_code(ir, current)    # decide + act
        has_more_static = (
            stage == "static"
            and bool(ir_dict.get("all_errors"))
            and any(
                (c["error_type"], c.get("error_message"), _orig_line(origin, c.get("line_number")))
                not in (skipped_static | {static_key})
                for c in ir_dict["all_errors"]
            )
        )
        if fixed == current or not fix_is_safe(current, fixed):
            entry["result"] = "explanation only (manual fix needed)"
            history.append(entry)
            if has_more_static:
                skipped_static.add(static_key)
                continue
            break
        if fixed in seen_states or repeats[sig] >= 3:         # patching in circles
            entry["result"] = "stuck (patch is not making progress)"
            history.append(entry)
            if has_more_static:
                skipped_static.add(static_key)
                continue
            break
        seen_states.add(fixed)
        entry["patch"] = _changed_lines(current, fixed)
        entry["result"] = "patched"
        history.append(entry)
        origin = _remap_origin(origin, current, fixed)        # keep the line map in step with the patch
        current = fixed                                       # observe on next iteration
    else:
        history.append({"step": "final",
                        "result": f"stopped: reached the {max_iters}-pass safety cap; errors may remain"})
    return current, history


def cpp_repair_loop(code, max_iters=30, time_budget=45, first_ir=None):
    """Iteratively apply safe fixes, checking each revision with the C++ compiler (-fsyntax-only)."""
    history, current = [], code
    seen_states = {code}
    skipped = set()
    origin = list(range(1, len(code.split("\n")) + 1))
    started = time.perf_counter()
    cached_ir = first_ir

    for step in range(max_iters):
        if time.perf_counter() - started > time_budget:
            history.append({"step": "final", "result": f"stopped: {time_budget}s time budget reached"})
            break
        ir = cached_ir if cached_ir is not None else extract_cpp_error(current)
        cached_ir = ir
        diagnostics = ir.get("all_errors") or ([ir] if ir.get("error_type") else [])
        if not diagnostics:
            history.append({"step": step + 1, "result": "clean"})
            return current, history, ir

        # Pick the first diagnostic not yet marked unfixable.
        diagnostic = None
        for cand in diagnostics:
            key = (cand.get("error_type"), cand.get("error_message"), _orig_line(origin, cand.get("line_number")))
            if key not in skipped:
                diagnostic = cand
                break
        if diagnostic is None:
            break

        line = diagnostic.get("line_number")
        orig_ln = _orig_line(origin, line)
        lines = current.split("\n")
        source = lines[line - 1].strip() if line and 1 <= line <= len(lines) else ""
        mistake, reason, guidance = explain_cpp_error(diagnostic)
        entry = {
            "step": step + 1,
            "error": diagnostic["error_type"],
            "line": line,
            "column": diagnostic.get("column"),
            "stage": "compiler",
            "source": source,
            "ir": diagnostic,
            "meaning": cpp_meaning(diagnostic["error_type"]),
            "mistake": mistake,
            "reason": reason,
            "guidance": guidance,
            "patch": [],
            "orig_line": orig_ln,
        }
        key = (diagnostic.get("error_type"), diagnostic.get("error_message"), orig_ln)
        fixed = apply_cpp_fix(current, {
            "error_type": diagnostic.get("error_type"),
            "message": diagnostic.get("error_message"),
            "line": line,
            "column": diagnostic.get("column"),
            "name": diagnostic.get("name"),
            "header": diagnostic.get("header"),
            "suggestion": diagnostic.get("suggestion"),
            "notes": diagnostic.get("notes", []),
        })
        if fixed == current or not fix_is_safe(current, fixed, language="cpp"):
            entry["result"] = "explanation only (manual fix needed)"
            history.append(entry)
            skipped.add(key)
            continue
        if fixed in seen_states:
            entry["result"] = "stopped: patch made no progress"
            history.append(entry)
            skipped.add(key)
            continue

        entry["patch"] = _changed_lines(current, fixed)
        entry["result"] = "patched"
        history.append(entry)
        seen_states.add(fixed)
        origin = _remap_origin(origin, current, fixed)
        current = fixed
        cached_ir = None
    else:
        history.append({"step": "final", "result": f"stopped: reached the {max_iters}-pass safety cap"})

    final_ir = cached_ir if cached_ir is not None else extract_cpp_error(current)
    if not final_ir.get("error_type"):
        history.append({"step": len(history) + 1, "result": "clean"})
    return current, history, final_ir


def build_cpp_issues(original_code, history):
    """Convert compiler repair history into the issue shape consumed by the web UI."""
    src_lines = original_code.split("\n")
    issues = []
    for entry in history:
        if not entry.get("error"):
            continue
        ir = entry["ir"]
        line = entry.get("orig_line")
        patched = entry["result"] == "patched"
        patch_list = entry.get("patch", [])
        issues.append({
            "id": len(issues) + 1,
            "line": line,
            "column": entry.get("column"),
            "type": entry["error"],
            "meaning": entry.get("meaning") or cpp_meaning(entry["error"]),
            "stage": "compiler",
            "source": src_lines[line - 1].strip() if line and line <= len(src_lines) else entry.get("source"),
            "mistake": entry.get("mistake") or entry.get("meaning", ""),
            "reason": entry["reason"],
            "how_to_fix": entry["guidance"],
            "suggestion": ir.get("suggestion"),
            "patched": patched,
            "status": entry["result"],
            "patch": [{"sign": sign, "text": text} for sign, text in patch_list],
            "hides_crash": patched and cpp_hides_crash(entry["error"], patch_list),
        })
    return issues


def analyze_cpp(code, sec_struct=None, sec_log=None, first_ir=None, scan_start=None):
    """Compile-check C++ and return corrections without executing untrusted binaries."""
    t0 = scan_start if scan_start is not None else time.perf_counter()
    fixed_code, history, final_ir = cpp_repair_loop(code, first_ir=first_ir)
    scan_ms = (time.perf_counter() - t0) * 1000
    errors_remain = bool(final_ir.get("error_type"))
    clean_check = any(entry.get("result") == "clean" for entry in history)
    if clean_check and not errors_remain:
        verdict = {
            "verdict": "VERIFIED" if fixed_code != code else "CLEAN",
            "detail": ("Patched C++ code passes compiler syntax & warning checks (-fsyntax-only)."
                       if fixed_code != code else "C++ compile check passed with no errors."),
        }
    elif fixed_code != code:
        rem_count = len(final_ir.get("all_errors") or [final_ir])
        verdict = {
            "verdict": "PARTIAL",
            "detail": f"Some errors were fixed, but {rem_count} compiler error(s) remain.",
        }
    else:
        verdict = {
            "verdict": "NO FIX GENERATED",
            "detail": "No safe automatic correction was available; see explanations to fix manually.",
        }
    issues = build_cpp_issues(code, history)
    compiler = final_ir.get("compiler") or (first_ir or {}).get("compiler")
    warnings = final_ir.get("warnings") or []
    summary = build_summary(issues, verdict)
    raw_lines = [
        f"[C++ COMPILER] {compiler or 'g++/clang++'} (-fsyntax-only -Wall -Wextra -std=c++17)",
        f"[VERDICT] {verdict['verdict']}: {verdict['detail']}",
    ]
    for iss in issues:
        raw_lines.append(f"  Line {iss['line']}: {iss['type']} [{iss['status']}] - {iss['mistake']}")
    return {
        "status": "success" if not issues and not errors_remain else "error_intercepted",
        "language": "cpp",
        "compiler": compiler,
        "analysis_note": f"Compile-checked using {compiler or 'C++ compiler'}. Press Run to compile and execute.",
        "warnings": [f"line {w.get('line', '?')}: {w.get('message', '')}" for w in warnings],
        "original_code": code,
        "fixed_code": fixed_code,
        "raw_text": "\n".join(raw_lines),
        "message": "C++ compile check passed cleanly. Press Run to compile and execute.",
        "issues": issues,
        "by_line": by_line(issues),
        "diagnostics": [entry["ir"] for entry in history if entry.get("error")],
        "verdict": verdict,
        "summary": summary,
        "metrics": build_metrics(final_ir),
        "metrics_data": build_metrics_data(scan_ms, final_ir),
        "blocked": False,
        "security": sec_struct or [],
        "security_alerts": sec_log or [],
        "notes": [h["result"] for h in history if not h.get("error") and h["result"] != "clean"],
    }



# ----------------------------------------------------------------------
# STRUCTURED OUTPUT FOR THE UI (replaces parsing the raw_text blob)
# ----------------------------------------------------------------------
def _hides_crash(etype, patch):
    text = " ".join(t for _, t in patch)
    return (etype in ("ZeroDivisionError", "KeyError", "IndexError", "ModuleNotFoundError", "ValueError")
            or "= None" in text or "TODO: define a real value" in text or "TODO: implement" in text)


def build_issues(original_code, history):
    """One dict per issue, in the order found. `line` is always an ORIGINAL-code line number."""
    src_lines = original_code.split("\n")
    issues = []
    for h in history:
        if not h.get("error"):
            continue
        parts = {}
        for ln in h["explanation"].split("\n"):                 # "Mistake: ..." / "Reason: ..." / "Fix: ..."
            k, _, v = ln.partition(": ")
            parts[k] = v
        line = h.get("orig_line")
        ir = h["ir"]
        patched = h["result"] == "patched"
        hides = patched and _hides_crash(h["error"], h.get("patch", []))
        issues.append({
            "id": len(issues) + 1,
            "line": line,                                         # highlight THIS line in the code panel
            "column": h.get("column"),
            "type": h["error"],                                   # e.g. NameError
            "meaning": explainer.meaning(h["error"]),            # one-line definition of the error
            "stage": h["stage"],                                  # parser | static | runtime
            "source": src_lines[line - 1].strip() if line and line <= len(src_lines) else h.get("source"),
            "mistake": parts.get("Mistake", ""),
            "reason": parts.get("Reason", ""),
            "how_to_fix": parts.get("Fix", ""),
            "suggestion": ir.get("suggestion"),                   # "did you mean ...?"
            "patched": patched,
            "status": h["result"],
            "patch": [{"sign": s_, "text": t} for s_, t in h.get("patch", [])],
            "hides_crash": hides,
        })
    return issues


def build_summary(issues, verdict):
    by_type, by_stage = Counter(i["type"] for i in issues), Counter(i["stage"] for i in issues)
    return {"total": len(issues),
            "fixed": sum(i["patched"] for i in issues),
            "unfixed": sum(not i["patched"] for i in issues),
            "by_type": dict(by_type), "by_stage": dict(by_stage),
            "verdict": verdict["verdict"], "detail": verdict["detail"]}


def by_line(issues):
    """{line: [issue ids]}: lets the UI show a count badge when one line has several errors."""
    out = {}
    for i in issues:
        if i["line"]:
            out.setdefault(i["line"], []).append(i["id"])
    return out


STAGE_LABEL = {"parser": "the parser", "static": "static analysis", "runtime": "runtime execution",
               "compiler": "the C++ compiler"}


def format_pipeline(sec_log, first_ir, history, verdict):
    """Overview of which compiler stage did what, so the static checker is VISIBLE in the output."""
    issues = [h for h in history if h.get("error")]
    parser = [h for h in issues if h["stage"] == "parser"]
    runtime = [h for h in issues if h["stage"] == "runtime"]
    ran_clean = any(h.get("result") == "clean" for h in history)
    patched = sum(h["result"] == "patched" for h in issues)

    # Every error the static checker found in its FIRST pass over the original code.
    static_errs = list((first_ir or {}).get("all_errors") or [])
    if not static_errs and (first_ir or {}).get("error_type") \
            and ((first_ir.get("traceback") or "").startswith("(static")):
        static_errs = [{"line_number": first_ir.get("line_number"), "column": 0,
                        "error_type": first_ir["error_type"], "error_message": first_ir.get("error_message")}]

    row = lambda n, label, text: f" {n}. {label:<22}: {text}\n"
    out = "[PIPELINE]\n"
    out += row(1, "Security scan", f"{len(sec_log)} non-blocking finding(s)" if sec_log
               else "passed, nothing suspicious")
    for line in sec_log:
        out += f"      {line}\n"
    if parser:
        out += row(2, "Parse + static check", "the parser rejected the file, so no AST (and no symbol table) was built")
    else:
        out += row(2, "Parse + static check",
                   f"{len(static_errs)} error(s) found in ONE pass, code NOT executed" if static_errs
                   else "no errors found (checked without running the code)")
        for e in static_errs:
            hint = f"  (did you mean '{e['suggestion']}'?)" if e.get("suggestion") else ""
            out += (f"      line {e['line_number']}, col {e['column']}: "
                    f"{e['error_type']}: {e['error_message']}{hint}\n")
    if runtime:
        out += row(3, "Sandbox execution", f"{len(runtime)} runtime error(s), only visible by running the code")
    elif ran_clean:
        out += row(3, "Sandbox execution", "ran cleanly, no runtime errors")
    else:
        out += row(3, "Sandbox execution", "not reached (stopped before the code could run)")
    out += row(4, "Repair loop", f"{patched} patch(es) over {len(issues)} pass(es)")
    out += row(5, "Verification", verdict["verdict"])
    return out


def format_diagnosis(history):
    """One block per issue: its IR summary, explanation and patch, then the final re-check."""
    issues = [h for h in history if h.get("error")]
    patched = sum(h["result"] == "patched" for h in issues)
    out = f"[DIAGNOSIS] {len(issues)} issue(s) found, {patched} patched\n"
    row = lambda label, text: (f"  {label:<7} : {text}\n" if label      # aligned "Label   : text" rows
                               else f"  {'':<7}   {text}\n")                 # continuation line, no label
    for n, h in enumerate(issues, 1):
        loc = f"line {h['line']}" + (f", col {h['column']}" if h.get("column") is not None else "")
        out += f"\nIssue {n} of {len(issues)}: {h['error']} ({loc}, found by {STAGE_LABEL[h['stage']]})\n"
        out += row("Code", h["source"])
        ir = h["ir"]
        out += row("IR", (f"node={ir.get('ast_node')}, parent={ir.get('parent_node')}, "
                          f"indent={ir.get('indentation_level')}, phase={ir.get('phase')}")
                   if ir.get("ast_node") else f"no AST node (file did not parse), phase={ir.get('phase')}")
        for ln in h["explanation"].split("\n"):              # Mistake / Reason / Fix
            label, _, text = ln.partition(": ")
            out += row(label, text)
        if h["trace"]:
            out += row("Trace", " > ".join(h["trace"]))
        for k, (sign, text) in enumerate(h["patch"]):
            out += row("Patch" if k == 0 else "", f"{sign} {text}")
        out += row("Result", h["result"])
    if len(issues) > 1:
        out += "\nNote: line numbers refer to the code as patched by the earlier issues.\n"
    for h in history:
        if not h.get("error"):
            out += ("\nFinal re-check: clean, no errors remain.\n" if h["result"] == "clean"
                    else f"\nNote: {h['result']}\n")
    return out


app = Flask(__name__)
CORS(app)
explainer = NLPExplainer()


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/files', methods=['GET'])
def get_files():
    return jsonify({"files": _available_test_files()})


@app.route('/api/source', methods=['GET'])
def get_source():
    """Read-only: returns file text WITHOUT running anything."""
    filename = safe_name(request.args.get('filename'))
    if not filename:
        return jsonify({"error": "File not found"}), 404
    return jsonify({"filename": filename, "code": read_source(filename)})


@app.route('/api/file', methods=['POST'])
def read_file():
    """Same as /api/source but POST + 'original_code' key (what index.html's selectFile expects)."""
    filename = safe_name((request.json or {}).get('filename'))
    if not filename:
        return jsonify({"error": "File not allowed"}), 404
    return jsonify({"original_code": read_source(filename)})


@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    t_req = time.perf_counter()
    data = request.json or {}
    filename = safe_name(data.get('filename'))
    posted = data.get('code')
    explicit_lang = data.get('language')
    # The UI can now send the (possibly edited) code directly. It goes through exactly the same
    # security scan + sandbox as /api/execute, so this opens nothing new.
    if isinstance(posted, str):
        code = posted
    elif filename:
        code = read_source(filename)
    else:
        return jsonify({"error": "File not found"}), 404
    if len(code.encode("utf-8", "ignore")) > MAX_CODE_BYTES:
        return jsonify({"error": "Input too large"}), 413

    lang = detect_language(filename=filename or data.get('filename'), code=code, explicit=explicit_lang)

    # ---- STAGE 0: security gate. Runs BEFORE anything compiles or executes. ----
    vulns, sec_log, blocked = scan(code, language=lang)
    sec_struct = [{"line": v["line"], "severity": v["severity"], "type": v["type"], "message": v["message"]}
                  for v in vulns]
    if blocked:
        return jsonify({
            "status": "blocked",
            "language": lang,
            "original_code": code,
            "raw_text": "[SECURITY] Execution BLOCKED. Critical/High findings:\n  " + "\n  ".join(sec_log),
            "metrics": "Not executed (blocked by security scan).",
            "metrics_data": build_metrics_data((time.perf_counter() - t_req) * 1000),
            "blocked": True,
            "security": sec_struct,          # UI: red banner + highlight these lines
            "issues": [], "by_line": {},
            "summary": {"total": 0, "fixed": 0, "unfixed": 0, "by_type": {}, "by_stage": {},
                        "verdict": "BLOCKED", "detail": "Not run: security scan found critical/high risks."},
        })

    # ---- C++ PIPELINE ----
    if lang == "cpp":
        try:
            first_ir = extract_cpp_error(code)
            result = analyze_cpp(code, sec_struct=sec_struct, sec_log=sec_log,
                                 first_ir=first_ir, scan_start=t_req)
        except CompilerNotFound as e:
            return jsonify({"status": "error", "error": str(e)}), 503
        return jsonify(result)

    # ---- PYTHON PIPELINE: static analysis, then sandboxed run (inside extract_error) ----
    try:
        ir_dict = extract_error(code)
    except RuntimeError as e:          # sandbox child died unexpectedly
        return jsonify({"status": "error", "error": f"Sandbox failure: {e}"}), 500

    if ir_dict and ir_dict.get("error_type"):
        error_type = ir_dict["error_type"]
        tb = ir_dict.get("traceback") or ""
        # Category = which compiler stage found it. Useful field for your IR diagram.
        category = "static" if tb.startswith("(static") else "runtime"

        fixed_code, repair_history = repair_loop(code, first_ir=ir_dict)   # agent: explain + patch each issue
        if not fix_is_safe(code, fixed_code):
            fixed_code = code
            repair_history.append({"step": "final", "result": "rejected by patch safety check"})

        verdict = verify_fix(code, fixed_code)
        issues = build_issues(code, repair_history)
        scan_ms = (time.perf_counter() - t_req) * 1000

        log_text = format_pipeline(sec_log, ir_dict, repair_history, verdict)
        log_text += "\n" + format_diagnosis(repair_history)
        total_explain = sum(h.get("explain_ms", 0) for h in repair_history)
        log_text += f"\n[PERFORMANCE] Explanation time: {total_explain:.3f} ms total\n"
        log_text += "\n[FIX VERIFICATION] (patch re-analyzed and re-executed in sandbox)\n"
        log_text += f"Verdict : {verdict['verdict']}\n"
        log_text += f"Detail  : {verdict['detail']}\n"

        return jsonify({
            "status": "error_intercepted",
            "language": "python",
            "original_code": code,
            "raw_text": log_text,
            "diagnostics": [h["ir"] for h in repair_history if h.get("error")],   # full IR JSON, one per issue
            "fixed_code": fixed_code,
            "metrics": build_metrics(ir_dict),
            "metrics_data": build_metrics_data(scan_ms, ir_dict),
            # ---- structured data for the new UI ----
            "blocked": False,
            "security": sec_struct,
            "issues": issues,
            "by_line": by_line(issues),
            "verdict": verdict,
            "summary": build_summary(issues, verdict),
            "notes": [h["result"] for h in repair_history if not h.get("error") and h["result"] != "clean"],
        })

    # No error found
    scan_ms = (time.perf_counter() - t_req) * 1000
    out_msg = "Execution completed normally. No compilation or runtime errors intercepted."
    captured = (ir_dict or {}).get("stdout", "")
    if captured and captured.strip():
        out_msg += f"\n\n[STDOUT OUTPUT]:\n{captured.strip()}"
    return jsonify({
        "status": "success",
        "language": "python",
        "original_code": code,
        "message": out_msg,
        "fixed_code": code,
        "security_alerts": sec_log,
        "metrics": build_metrics(ir_dict),
        "metrics_data": build_metrics_data(scan_ms, ir_dict),
        "blocked": False, "security": sec_struct, "issues": [], "by_line": {},
        "summary": {"total": 0, "fixed": 0, "unfixed": 0, "by_type": {}, "by_stage": {},
                    "verdict": "CLEAN", "detail": "No errors found."},
    })


@app.route('/api/execute', methods=['POST'])
def execute_code():
    data = request.json or {}
    code_to_run = data.get('code', '')
    if len(code_to_run.encode("utf-8", "ignore")) > MAX_CODE_BYTES:
        return jsonify({"output": "BLOCKED: input too large."})
    lang = detect_language(filename=data.get('filename'), code=code_to_run, explicit=data.get('language'))
    _, _, blocked = scan(code_to_run, language=lang)
    if blocked:
        return jsonify({"output": "BLOCKED: critical security findings, code not executed."})

    try:
        if lang == "cpp":
            execution = run_cpp_code(code_to_run)
        else:
            execution = run_code(code_to_run)     # child process + 5s timeout
    except (RuntimeError, CompilerNotFound) as e:
        return jsonify({"output": f"Sandbox failure: {e}"})

    output = execution["stdout"]
    if execution["error_type"]:
        prefix = "COMPILE / EXECUTION ERROR" if lang == "cpp" else "CRASH DURING EXECUTION"
        output += (f"\n{prefix}:\n"
                   f"{execution['error_type']}: {execution['error_message']}")
    elif not output.strip():
        output = "Code executed cleanly (No standard output returned)."
    return jsonify({"output": output, "language": lang})


@app.route('/api/save', methods=['POST'])
def save_file():
    data = request.json or {}
    code = data.get('code')
    if not isinstance(code, str):
        return jsonify({"error": "Code must be text"}), 400
    if len(code.encode("utf-8", "ignore")) > MAX_CODE_BYTES:
        return jsonify({"error": "Input too large"}), 413

    lang = detect_language(filename=data.get('filename'), code=code, explicit=data.get('language'))
    # Never persist code with critical findings.
    if scan(code, language=lang)[2]:
        return jsonify({"error": "Refusing to save code with critical security findings"}), 400

    if data.get('create') is True:
        requested_name = data.get('filename')
        if not isinstance(requested_name, str):
            return jsonify({"error": "Enter a valid filename"}), 400
        raw_name = requested_name.strip()
        ext = ".cpp" if lang == "cpp" else ".py"
        stem = raw_name
        for candidate_ext in (".py",) + CPP_EXTENSIONS:
            if raw_name.lower().endswith(candidate_ext):
                ext = candidate_ext
                stem = raw_name[:-len(candidate_ext)]
                break
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,60}", stem):
            return jsonify({"error": "Use 1-60 letters, numbers, underscores, or hyphens for the filename"}), 400
        new_filename = f"test_user_{stem}{ext}"
        try:
            with open(new_filename, "x", encoding="utf-8") as f:
                f.write(code)
        except FileExistsError:
            return jsonify({"error": f"{new_filename} already exists"}), 409
        return jsonify({"status": "success", "new_filename": new_filename})

    original_filename = safe_name(data.get('filename'))   # must be an existing whitelisted file
    if not original_filename:
        return jsonify({"error": "Missing or invalid filename/code"}), 400

    # Always write to <name>_fixed<ext> so the original test file is never overwritten.
    base, ext = os.path.splitext(original_filename)
    new_filename = original_filename if base.endswith("_fixed") else f"{base}_fixed{ext}"

    with open(new_filename, "w", encoding="utf-8") as f:
        f.write(code)
    return jsonify({"status": "success", "new_filename": new_filename})


_bench_lock = threading.Lock()      # one benchmark at a time (each run executes test files in the sandbox)


def _run_benchmark(repeats):
    """Re-measure the real pipeline on the ground-truth test files and rewrite the CSV."""
    from types import SimpleNamespace
    from fix_benchmark import run_benchmark       # imported lazily: it must not import app (circular)
    api = SimpleNamespace(read_source=read_source, extract_error=extract_error, repair_loop=repair_loop,
                          fix_is_safe=fix_is_safe, verify_fix=verify_fix)
    return run_benchmark(api, repeats)


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Dashboard data. Every number comes from a measurement file or a live scan (see
    analytics_data.py); nothing is generated by formulas or random(). If no benchmark has been
    run yet, run a quick one-repeat benchmark first so the page is never empty."""
    import analytics_data
    if not os.path.exists(analytics_data.BENCH_CSV):
        if _bench_lock.acquire(blocking=False):
            try:
                _run_benchmark(repeats=1)
            finally:
                _bench_lock.release()
    return jsonify(analytics_data.build_payload())


@app.route('/api/analytics/refresh', methods=['POST'])
def refresh_analytics():
    import analytics_data
    if not _bench_lock.acquire(blocking=False):
        return jsonify({"error": "A benchmark is already running"}), 409
    try:
        _run_benchmark(repeats=3)                  # median of 3 runs per file
    finally:
        _bench_lock.release()
    return jsonify(analytics_data.build_payload())


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Saves an uploaded/pasted .py or .cpp/.cc/.cxx file as test_upload_<name><ext>. Does NOT run it.
    The prefix means (a) the existing whitelist lists it automatically and
    (b) an upload can never overwrite one of your real test files."""
    data = request.json or {}
    name = os.path.basename(data.get('filename') or 'pasted.py')   # strips any ../
    code = data.get('code')

    if not isinstance(code, str) or not code.strip():
        return jsonify({"error": "Empty file"}), 400
    allowed_exts = (".py",) + CPP_EXTENSIONS
    matched_ext = next((ext for ext in allowed_exts if name.lower().endswith(ext)), None)
    if not matched_ext:
        return jsonify({"error": "Only .py, .cpp, .cc, and .cxx files are accepted"}), 400
    if "\x00" in code:
        return jsonify({"error": "Null byte in source"}), 400      # ast.parse would raise ValueError
    if len(code.encode("utf-8", "ignore")) > MAX_CODE_BYTES:
        return jsonify({"error": "File too large (100 KB max)"}), 413

    # Whitelist characters in the stem so the name can't contain path tricks.
    raw_stem = name[:-len(matched_ext)]
    stem = re.sub(r'[^A-Za-z0-9_]', '_', raw_stem)[:40] or 'file'
    new_name = f"test_upload_{stem}{matched_ext}"
    with open(new_name, "w", encoding="utf-8") as f:
        f.write(code)
    return jsonify({"status": "success", "filename": new_name})

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


if __name__ == '__main__':
    import threading
    import webbrowser

    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:5001")

    threading.Thread(target=open_browser).start()
    # debug=False: Flask's debugger lets anyone who reaches the page run code on your machine.
    app.run(debug=False, port=5001, use_reloader=False)