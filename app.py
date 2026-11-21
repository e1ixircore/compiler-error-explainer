from collections import Counter
import difflib
import threading
import glob
import json
import os
import queue
import time
import re

from flask import Flask, Response, request, jsonify, render_template, stream_with_context
from flask_cors import CORS

from error_extractor import extract_error, run_code   # run_code = hardened sandbox
from sandbox import get_sandbox_status
from nlp_explainer import NLPExplainer
from ir_generator import IRGenerator
from security_analyzer import SecurityAnalyzer
from security_metrics_engine import SecurityMetricsEngine, METRICS_REGISTRY
from agentic_compiler import AgenticCompilerCoordinator, CompilerErrorObj
from static_analyzer import static_check
from cst_patcher import apply_single_issue_patch_cst
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
MAX_CODE_BYTES = 2_000_000 # allow large 2,000+ LOC benchmark files while still bounding input size


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


def _classify_test_file(fname: str) -> dict:
    base = os.path.basename(fname)
    is_bench = fname.startswith("benchmarks/")
    is_cpp = is_cpp_name(fname)
    is_sec = (
        base.startswith("test_sec")
        or base == "test_security.py"
        or base == "test_cpp_security.cpp"
        or base.startswith("sec_bench_")
    )
    if is_sec:
        group = "large_security" if is_bench else "standard_security"
    else:
        group = "large_error" if is_bench else "standard_error"
    return {
        "filename": fname,
        "is_fixed": "_fixed." in fname,
        "is_benchmark": is_bench,
        "is_security": is_sec,
        "suite_group": group,
        "language": "cpp" if is_cpp else "python",
    }


def _available_test_files():
    files = []
    for extension in (".py",) + CPP_EXTENSIONS:
        files.extend(glob.glob(f"test*{extension}"))
        files.extend(glob.glob(f"*_fixed{extension}"))
    for extension in (".py",) + CPP_EXTENSIONS:
        files.extend([f"benchmarks/{os.path.basename(p)}" for p in glob.glob(f"benchmarks/*{extension}")])
    all_files = sorted(set(files))
    excluded = {"test_ir.py", "test_nlp.py", "sample_input.py", "sample_input_fixed.py"}
    all_files = [f for f in all_files if f not in excluded]
    return [_classify_test_file(f) for f in all_files]


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
    """Whitelist check used by endpoints.
    Allows root test files and allowed benchmarks/ files."""
    if not name:
        return None
    allowed = {i["filename"] for i in _available_test_files()}
    return name if name in allowed else None


def read_source(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(filename, "r", encoding="latin-1") as f:
            return f.read()


_security_engine = SecurityMetricsEngine()

def _scan_with_report(code, language="python"):
    """Returns (vulns, formatted log lines, is_blocked, raw_report) using the 52-metric Security Engine."""
    rep = _security_engine.analyze(code, language=language)
    findings = rep.get("findings", [])
    vulns = [
        {
            "line": f.get("line", 1),
            "severity": f.get("severity", "MEDIUM"),
            "type": f.get("type", "Security Finding"),
            "metric_id": f.get("metric_id", ""),
            "cwe": f.get("cwe", ""),
            "message": f.get("message", ""),
        }
        for f in findings
    ]
    log = [f"[{v['severity']}] Line {v['line']} ({v['metric_id']}): {v['message']}" for v in vulns]
    blocked = rep.get("summary", {}).get("blocked", False) or any(v["severity"] in BLOCKING for v in vulns)
    return vulns, log, blocked, rep


def scan(code, language="python"):
    """Returns (vulns, formatted log lines, is_blocked) using the 52-metric Security Engine."""
    vulns, log, blocked, _ = _scan_with_report(code, language=language)
    return vulns, log, blocked


def _compute_line_fixes(code, hardened):
    """Map 1-based original line numbers to their hardened line text, even when imports are inserted."""
    orig_lines = code.splitlines()
    hard_lines = hardened.splitlines()
    line_fixes = {}
    if len(orig_lines) == len(hard_lines):
        for idx, (o_ln, h_ln) in enumerate(zip(orig_lines, hard_lines), start=1):
            if o_ln != h_ln:
                line_fixes[idx] = h_ln.strip()
        return line_fixes
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, orig_lines, hard_lines, autojunk=False).get_opcodes():
        if tag == "replace":
            old_len = i2 - i1
            new_len = j2 - j1
            # If extra lines (e.g. inserted imports) precede the replaced lines at the start, align from the tail
            offset = (new_len - old_len) if (i1 == 0 and new_len > old_len) else 0
            for k in range(old_len):
                j = j1 + offset + k
                if j1 <= j < j2:
                    line_fixes[i1 + k + 1] = hard_lines[j].strip()
    return line_fixes


def build_security_solution(code, language="python", hardened=None, actions=None, after_rep=None, audit_rep=None):
    """When Stage 1 Security Gate blocks execution, synthesize a hardened version of the code
    so the user can either apply the security solution or stop diagnosis."""
    if hardened is None:
        if audit_rep is None:
            audit_rep = _security_engine.analyze(code, language=language)
        synth = AgenticCompilerCoordinator().synthesizer
        if language == "cpp":
            hardened, actions = synth.harden_cpp_security(code, audit_rep)
        else:
            hardened, actions = synth.harden_python_security(code, audit_rep)
    actions = actions or []
    if after_rep is None:
        after_rep = _security_engine.analyze(hardened, language=language)
    still_blocked = after_rep.get("summary", {}).get("blocked", False)
    line_fixes = _compute_line_fixes(code, hardened) if hardened != code else {}
    return {
        "can_sanitize": (hardened != code) and not still_blocked,
        "has_partial_fix": (hardened != code),
        "hardened_code": hardened if hardened != code else "",
        "actions": actions,
        "line_fixes": line_fixes,
        "remaining_blocking": after_rep.get("severity_counts", {}).get("CRITICAL", 0)
        + after_rep.get("severity_counts", {}).get("HIGH", 0),
    }


def _measure_efficiency(code, language="python", run_ms=0.0):
    """Evaluate AST complexity and loop nesting depth when code is executable."""
    import ast as _ast
    avg_cc = 1.0
    max_loop_depth = 0
    if language == "python":
        try:
            tree = _ast.parse(code)
            funcs = [n for n in _ast.walk(tree) if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef))]
            if funcs:
                ccs = []
                for fn in funcs:
                    cc = 1
                    for sub in _ast.walk(fn):
                        if isinstance(sub, (_ast.If, _ast.For, _ast.AsyncFor, _ast.While, _ast.ExceptHandler, _ast.IfExp)):
                            cc += 1
                    ccs.append(cc)
                avg_cc = round(sum(ccs) / len(ccs), 1)

            def _depth(node, cur=0):
                nonlocal max_loop_depth
                if isinstance(node, (_ast.For, _ast.AsyncFor, _ast.While)):
                    cur += 1
                    if cur > max_loop_depth:
                        max_loop_depth = cur
                for ch in _ast.iter_child_nodes(node):
                    _depth(ch, cur)

            _depth(tree, 0)
        except Exception:
            pass
    pts = 15
    notes = []
    if max_loop_depth >= 3:
        pts -= 3
        notes.append(f"nested loops (depth {max_loop_depth})")
    elif max_loop_depth == 2:
        pts -= 1
    if avg_cc > 12:
        pts -= 3
        notes.append(f"high avg branch complexity ({avg_cc})")
    elif avg_cc > 8:
        pts -= 1
    if run_ms and run_ms > 500:
        pts -= 2
        notes.append(f"runtime {run_ms:.0f} ms")
    pts = max(5, min(15, pts))
    detail = f"Executable ({pts}/15 pts · avg complexity {avg_cc}, loop depth {max_loop_depth})"
    if notes:
        detail += " — " + ", ".join(notes)
    return {
        "score": pts,
        "max": 15,
        "evaluated": True,
        "avg_cyclomatic": avg_cc,
        "max_loop_depth": max_loop_depth,
        "run_ms": run_ms,
        "status": detail,
    }


def compute_code_score(code, language, vulns, blocked, issues, executable=False, run_ms=0.0, fixed_code=None):
    """
    Transparent 3-Pillar Compiler Score on the CURRENT code in the editor:
      1. Security (0 - 40 pts)      : Stage 1 gate. If CRITICAL/HIGH -> 0/40 and total score = 0 (Grade F - Blocked).
      2. Errors   (0 - 45 pts)      : Stage 2 diagnosis. Deducts by error count and severity (Syntax, Runtime, Static, Logical).
      3. Efficiency (0 - 15 pts)    : Stage 3 quality. Evaluated ONLY when the current code is executable (0 errors & not blocked).
    """
    if blocked:
        n_crit = sum(1 for v in vulns if v.get("severity") == "CRITICAL")
        n_high = sum(1 for v in vulns if v.get("severity") == "HIGH")
        return {
            "total_score": 0,
            "grade": "F",
            "grade_label": "Grade F · Blocked by Security",
            "blocked": True,
            "security": {
                "score": 0,
                "max": 40,
                "status": f"BLOCKED ({n_crit} Critical, {n_high} High threat(s)) — Diagnosis halted at Stage 1",
            },
            "errors": {
                "score": 0,
                "max": 45,
                "count": 0,
                "status": "Stopped — Resolve security threat first before static/runtime diagnosis",
            },
            "efficiency": {
                "score": 0,
                "max": 15,
                "evaluated": False,
                "status": "Not executed (blocked by Security Gate)",
            },
            "projected": None,
        }

    # 1. Security Pillar (40 pts)
    n_med = sum(1 for v in vulns if v.get("severity") == "MEDIUM")
    n_low = sum(1 for v in vulns if v.get("severity") in ("LOW", "INFO"))
    sec_pts = max(16, 40 - 6 * n_med - 3 * n_low)
    sec_status = "Passed (40/40 · No security threats)" if not vulns else f"Passed ({sec_pts}/40 · {len(vulns)} non-blocking security note(s))"

    # 2. Errors / Correctness Pillar (45 pts) — Proportional to LOC & Error Severity Density
    import math as _math
    loc = max(1, len(code.splitlines()))
    eff_scale = max(10.0, _math.sqrt(loc * 10.0))

    def _weighted_err_score(err_list):
        if not err_list:
            return 45, 0.0
        w_sum = 0.0
        for iss in err_list:
            et = iss.get("type", "")
            st = iss.get("stage", "")
            if et in ("SyntaxError", "IndentationError") or st == "parser":
                w_sum += 1.5
            elif st == "runtime":
                w_sum += 1.2
            elif et == "LogicalError":
                w_sum += 0.7
            else:
                w_sum += 1.0
        pts = min(44, int(round(45.0 * _math.exp(-3.2 * (w_sum / eff_scale)))))
        return max(0, pts), w_sum

    n_issues = len(issues)
    density_per_100 = round((n_issues / loc) * 100.0, 2)
    if n_issues == 0:
        err_pts = 45
        err_status = f"Clean (0 errors across {loc:,} LOC)"
    else:
        err_pts, w_sum = _weighted_err_score(issues)
        err_status = f"{n_issues} error(s) · {density_per_100}/100 LOC ({err_pts}/45)"

    # 3. Efficiency Pillar (15 pts) — only evaluated when current code is executable (0 errors)
    if n_issues == 0 and executable:
        eff_obj = _measure_efficiency(code, language=language, run_ms=run_ms)
    else:
        eff_obj = {
            "score": 0,
            "max": 15,
            "evaluated": False,
            "status": "Not executable yet (fix the errors above to run & measure efficiency)",
        }

    total_score = sec_pts + err_pts + eff_obj["score"]
    if n_issues > 0:
        # A file that still has unapplied errors in the editor cannot receive Grade A
        total_score = min(total_score, 84)

    if total_score >= 90 and n_issues == 0:
        grade = "A"
    elif total_score >= 75:
        grade = "B"
    elif total_score >= 60:
        grade = "C"
    elif total_score >= 40:
        grade = "D"
    else:
        grade = "F"

    projected = None
    if fixed_code and fixed_code != code and n_issues > 0:
        unfixed_list = [iss for iss in issues if not iss.get("patched")]
        n_unfixed = len(unfixed_list)
        if n_unfixed == 0:
            proj_eff = _measure_efficiency(fixed_code, language=language, run_ms=run_ms)["score"]
            proj_total = sec_pts + 45 + proj_eff
            proj_grade = "A" if proj_total >= 90 else "B"
        else:
            proj_err_pts, _ = _weighted_err_score(unfixed_list)
            proj_total = min(84, sec_pts + proj_err_pts)
            proj_grade = "B" if proj_total >= 75 else ("C" if proj_total >= 60 else "D")
        projected = {
            "score": proj_total,
            "grade": proj_grade,
            "unfixed_remaining": n_unfixed,
        }

    return {
        "total_score": total_score,
        "grade": grade,
        "grade_label": f"Grade {grade} · {total_score}/100",
        "blocked": False,
        "loc": loc,
        "defect_density_per_100_loc": density_per_100,
        "security": {"score": sec_pts, "max": 40, "status": sec_status},
        "errors": {"score": err_pts, "max": 45, "count": n_issues, "density": density_per_100, "status": err_status},
        "efficiency": eff_obj,
        "projected": projected,
    }


def fix_is_safe(original, fixed, language="python"):
    """A patch may never ADD a vulnerability class that the original didn't have."""
    cmp_res = _security_engine.compare(original, fixed, language=language)
    return bool(cmp_res.get("patch_safe", True))

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
    a, b = before.split("\n"), after.split("\n")
    if len(a) == len(b):
        diffs = [(x, y) for x, y in zip(a, b) if x != y]
        if len(diffs) <= 6:
            out = []
            for x, y in diffs:
                out.append(("-", x.strip()))
                out.append(("+", y.strip()))
            return out
    diff = list(difflib.unified_diff(a, b, lineterm="", n=0))
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
    if len(a) == len(b):
        return origin
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
    handled_static = set()               # static error keys already patched or skipped in current batch
    cached_static_ir = None              # reuse static_check batch when patches don't shift line numbers
    t_start = time.perf_counter()
    origin = list(range(1, len(code.split("\n")) + 1))   # line i of `current` came from original line origin[i]
    synthesizer = AgenticCompilerCoordinator().synthesizer
    for i in range(max_iters):
        if time.perf_counter() - t_start > time_budget:
            history.append({"step": "final",
                            "result": f"stopped: {time_budget}s time budget reached; errors may remain"})
            break

        # Reuse cached static batch if unhandled errors remain in it
        if cached_static_ir is not None:
            has_unhandled = any(
                (c["error_type"], c.get("error_message"), _orig_line(origin, c.get("line_number")))
                not in (skipped_static | handled_static)
                for c in (cached_static_ir.get("all_errors") or [])
            )
            if has_unhandled:
                ir_dict = cached_static_ir
            else:
                cached_static_ir = None
                ir_dict = extract_error(current)
        else:
            ir_dict = first_ir if (i == 0 and first_ir is not None) else extract_error(current)

        if not ir_dict.get("error_type"):
            history.append({"step": i + 1, "result": "clean"})
            break
        tb = ir_dict.get("traceback") or ""
        stage = "static" if tb.startswith("(static") else "runtime"
        if ir_dict["error_type"] in ("SyntaxError", "IndentationError"):
            stage = "parser"             # rejected before any AST existed

        # If static analysis found multiple errors, iterate through all unhandled static errors cleanly
        active = ir_dict
        if stage == "static":
            all_static = ir_dict.get("all_errors") or [ir_dict]
            if cached_static_ir is None and len(all_static) > 1:
                cached_static_ir = ir_dict
            picked = None
            for cand in all_static:
                key = (cand["error_type"], cand.get("error_message"), _orig_line(origin, cand.get("line_number")))
                if key not in (skipped_static | handled_static):
                    picked = cand
                    break
            if picked is None:
                cached_static_ir = None
                # All static/logical errors in `current` have already been reported.
                # Now run `current` in the isolated sandbox so any runtime errors are ALSO discovered and patched!
                try:
                    run_res = run_code(current)
                except Exception:
                    break
                if not run_res.get("error_type"):
                    break
                r_orig_ln = _orig_line(origin, run_res.get("line_number"))
                if any(sk[2] == r_orig_ln for sk in skipped_static):
                    break
                active = dict(
                    ir_dict,
                    error_type=run_res["error_type"],
                    error_message=run_res.get("error_message"),
                    line_number=run_res.get("line_number"),
                    column=None,
                    suggestion=None,
                    traceback=run_res.get("traceback") or "",
                )
                tb = active["traceback"]
                stage = "runtime"
            else:
                active = dict(
                    ir_dict,
                    error_type=picked["error_type"],
                    error_message=picked.get("error_message"),
                    line_number=picked.get("line_number"),
                    column=picked.get("column"),
                    suggestion=picked.get("suggestion"),
                )

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

        # Use Agentic AI Compiler Contextual Synthesizer as primary fix generator
        err_obj = CompilerErrorObj(
            ir["error_type"],
            ir.get("error_message") or "",
            ln or 1,
            stage,
            tb,
            suggestion=active.get("suggestion"),
        )
        fixed, ai_expl, ai_action = synthesizer.repair_functional_bug(
            current, err_obj, language="python", precomputed_ir=ir
        )
        if ai_expl and not explanation:
            explanation = ai_expl
            entry["explanation"] = ai_expl

        # Fallback to rule generator if agentic pass produced identical code
        if fixed == current:
            fixed = explainer.generate_fixed_code(ir, current)

        diff_lines = _changed_lines(current, fixed) if fixed != current else []
        added_snip = "\n".join(t for s_, t in diff_lines if s_ == "+")
        step_safe = (fixed != current) and (not added_snip or not scan(added_snip, "python")[2])

        if fixed == current or not step_safe:
            entry["result"] = "explanation only (manual fix needed)"
            history.append(entry)
            if stage == "static":
                skipped_static.add(static_key)
                continue
            break
        if fixed in seen_states or repeats[sig] >= 3:         # patching in circles
            entry["result"] = "stuck (patch is not making progress)"
            history.append(entry)
            if stage == "static":
                skipped_static.add(static_key)
                continue
            break
        seen_states.add(fixed)
        entry["patch"] = diff_lines
        entry["result"] = "patched"
        history.append(entry)
        if stage == "static":
            handled_static.add(static_key)
        if fixed.count("\n") != current.count("\n"):
            cached_static_ir = None
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
    mdata = build_metrics_data(scan_ms, final_ir)
    score_data = compute_code_score(
        code, "cpp", sec_struct or [], False, issues,
        executable=(len(issues) == 0 and not errors_remain),
        run_ms=mdata.get("run_ms", 0.0),
        fixed_code=fixed_code,
    )
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
        "score_data": score_data,
        "metrics": build_metrics(final_ir),
        "metrics_data": mdata,
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
        plus_lines = [t for s_, t in h.get("patch", []) if s_ == "+"]
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
            "error_message": ir.get("error_message", ""),
            "error_variable": ir.get("error_variable"),
            "patched": patched,
            "is_ambiguous": not patched,
            "ai_fix_line": plus_lines[-1] if plus_lines else "",
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
app.config["TEMPLATES_AUTO_RELOAD"] = True
CORS(app)
explainer = NLPExplainer()


@app.after_request
def _no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response


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


def _format_sse(event_name, data):
    """Format a single Server-Sent Event frame."""
    return f"event: {event_name}\ndata: {json.dumps(data)}\n\n"


def _build_agentic_analyze_payload(code, lang, coord_res, vulns, sec_struct, sec_log, blocked, t_req):
    """Build the unified Web Studio /api/analyze payload from AgenticCompilerCoordinator.compile_and_harden()."""
    scan_ms = (time.perf_counter() - t_req) * 1000
    agent_trace = coord_res.get("agent_trace") or []
    iteration_history = coord_res.get("iteration_history") or []
    agentic_meta = {
        "converged": coord_res.get("converged", False),
        "pass_at_k": coord_res.get("pass_at_k"),
        "iterations_used": coord_res.get("iterations_used", 0),
        "execution_verified": coord_res.get("execution_verified", False),
        "prompt_injections_detected": coord_res.get("prompt_injections_detected", 0),
        "rejected_patches": coord_res.get("rejected_patches", 0),
        "actions_applied": coord_res.get("actions_applied", []),
        "risk_reduction_pct": coord_res.get("risk_reduction_pct", 0.0),
        "health_improvement": coord_res.get("health_improvement", 0.0),
        "resolved_metrics": coord_res.get("resolved_metrics", []),
        "security_regressions": coord_res.get("security_regressions", []),
        "initial_summary": coord_res.get("initial_summary", {}),
        "final_summary": coord_res.get("final_summary", {}),
        "total_time_ms": coord_res.get("total_time_ms", round(scan_ms, 3)),
    }

    # ---- STAGE 1: SECURITY GATE (Critical/High threats detected in original code) ----
    if blocked:
        compiled = coord_res.get("compiled_code")
        if compiled is not None and coord_res.get("final_audit") is not None:
            sec_solution = build_security_solution(
                code,
                language=lang,
                hardened=compiled,
                actions=coord_res.get("actions_applied", []),
                after_rep=coord_res.get("final_audit"),
            )
        else:
            sec_solution = build_security_solution(code, language=lang)
        if not sec_solution.get("hardened_code") and compiled and compiled != code:
            sec_solution["hardened_code"] = compiled
        score_data = compute_code_score(code, lang, vulns, True, [], executable=False)
        return {
            "status": "blocked",
            "language": lang,
            "original_code": code,
            "raw_text": "[STAGE 1 SECURITY GATE] Execution & Error Diagnosis BLOCKED. Critical/High findings:\n  " + "\n  ".join(sec_log),
            "metrics": "Stopped at Stage 1 Security Gate.",
            "metrics_data": build_metrics_data(scan_ms),
            "blocked": True,
            "security": sec_struct,
            "security_solution": sec_solution,
            "score_data": score_data,
            "issues": [],
            "by_line": {},
            "agent_trace": agent_trace,
            "iteration_history": iteration_history,
            "agentic": agentic_meta,
            "summary": {
                "total": 0,
                "fixed": 0,
                "unfixed": 0,
                "by_type": {},
                "by_stage": {},
                "verdict": "BLOCKED",
                "detail": f"Stage 1 Security Gate intercepted {len(sec_struct)} critical/high security threat(s). Error diagnosis halted until resolved.",
            },
        }

    repair_history = coord_res.get("repair_history") or []
    fixed_code = coord_res.get("compiled_code", code)
    first_ir = coord_res.get("first_ir")
    final_ir = coord_res.get("final_ir")

    # ---- STAGE 2A: C++ RESULT (from AgenticCompilerCoordinator) ----
    if lang == "cpp":
        errors_remain = bool((final_ir or {}).get("error_type"))
        clean_check = coord_res.get("converged", False) or any(e.get("result") == "clean" for e in repair_history)
        if clean_check and not errors_remain:
            verdict = {
                "verdict": "VERIFIED" if fixed_code != code else "CLEAN",
                "detail": ("Patched C++ code passes compiler syntax & warning checks (-fsyntax-only)."
                           if fixed_code != code else "C++ compile check passed with no errors."),
            }
        elif fixed_code != code:
            rem_count = len((final_ir or {}).get("all_errors") or ([final_ir] if final_ir else []))
            verdict = {
                "verdict": "PARTIAL",
                "detail": f"Some errors were fixed, but {rem_count} compiler error(s) remain.",
            }
        else:
            verdict = {
                "verdict": "NO FIX GENERATED",
                "detail": "No safe automatic correction was available; see explanations to fix manually.",
            }
        issues = build_cpp_issues(code, repair_history)
        compiler = (final_ir or {}).get("compiler") or (first_ir or {}).get("compiler")
        warnings = (final_ir or {}).get("warnings") or []
        summary = build_summary(issues, verdict)
        mdata = build_metrics_data(scan_ms, final_ir)
        score_data = compute_code_score(
            code, "cpp", sec_struct, False, issues,
            executable=(len(issues) == 0 and not errors_remain),
            run_ms=mdata.get("run_ms", 0.0),
            fixed_code=fixed_code,
        )
        raw_lines = [
            f"[5-AGENT COMPILER · C++] {compiler or 'g++/clang++'} (-fsyntax-only -Wall -Wextra -std=c++17)",
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
            "diagnostics": [e["ir"] for e in repair_history if e.get("error")],
            "verdict": verdict,
            "summary": summary,
            "score_data": score_data,
            "metrics": build_metrics(final_ir),
            "metrics_data": mdata,
            "blocked": False,
            "security": sec_struct,
            "security_alerts": sec_log,
            "agent_trace": agent_trace,
            "iteration_history": iteration_history,
            "agentic": agentic_meta,
            "notes": [h["result"] for h in repair_history if not h.get("error") and h["result"] != "clean"],
        }

    # ---- STAGE 2B: PYTHON RESULT (from AgenticCompilerCoordinator) ----
    patch_safe = coord_res.get("patch_safe")
    if patch_safe is None:
        patch_safe = fix_is_safe(code, fixed_code)
    if not patch_safe:
        fixed_code = code
        repair_history.append({"step": "final", "result": "rejected by patch safety check"})

    error_entries = [h for h in repair_history if h.get("error")]
    if error_entries or (first_ir and first_ir.get("error_type")):
        if coord_res.get("converged") and fixed_code != code:
            verdict = {
                "verdict": "VERIFIED",
                "detail": "Patched code re-analyzed and executed cleanly in sandbox (Pass@{}).".format(
                    coord_res.get("pass_at_k") or 1
                ),
            }
        else:
            verdict = verify_fix(code, fixed_code)

        issues = build_issues(code, repair_history)
        mdata = build_metrics_data(scan_ms, first_ir or final_ir)
        score_data = compute_code_score(
            code, "python", vulns, False, issues,
            executable=False,
            run_ms=mdata.get("run_ms", 0.0),
            fixed_code=fixed_code,
        )

        log_text = format_pipeline(sec_log, first_ir, repair_history, verdict)
        log_text += "\n" + format_diagnosis(repair_history)
        total_explain = sum(h.get("explain_ms", 0) for h in repair_history)
        log_text += f"\n[PERFORMANCE] Explanation time: {total_explain:.3f} ms total\n"
        log_text += "\n[FIX VERIFICATION] (5-Agent Coordinator + Isolated Sandbox)\n"
        log_text += f"Verdict : {verdict['verdict']}\n"
        log_text += f"Detail  : {verdict['detail']}\n"

        return {
            "status": "error_intercepted",
            "language": "python",
            "original_code": code,
            "raw_text": log_text,
            "diagnostics": [h["ir"] for h in repair_history if h.get("error")],
            "fixed_code": fixed_code,
            "metrics": build_metrics(first_ir or final_ir),
            "metrics_data": mdata,
            "score_data": score_data,
            "blocked": False,
            "security": sec_struct,
            "issues": issues,
            "by_line": by_line(issues),
            "verdict": verdict,
            "summary": build_summary(issues, verdict),
            "agent_trace": agent_trace,
            "iteration_history": iteration_history,
            "agentic": agentic_meta,
            "notes": [h["result"] for h in repair_history if not h.get("error") and h["result"] != "clean"],
        }

    # No error found — code executed cleanly!
    mdata = build_metrics_data(scan_ms, final_ir or first_ir)
    score_data = compute_code_score(
        code, "python", vulns, False, [],
        executable=True,
        run_ms=mdata.get("run_ms", 0.0),
        fixed_code=fixed_code,
    )
    out_msg = "Execution completed normally. No compilation or runtime errors intercepted."
    captured = coord_res.get("execution_output") or ((final_ir or {}).get("stdout") or "")
    if captured and captured.strip():
        out_msg += f"\n\n[STDOUT OUTPUT]:\n{captured.strip()}"
    return {
        "status": "success",
        "language": "python",
        "original_code": code,
        "message": out_msg,
        "fixed_code": fixed_code,
        "security_alerts": sec_log,
        "metrics": build_metrics(final_ir or first_ir),
        "metrics_data": mdata,
        "score_data": score_data,
        "blocked": False,
        "security": sec_struct,
        "issues": [],
        "by_line": {},
        "agent_trace": agent_trace,
        "iteration_history": iteration_history,
        "agentic": agentic_meta,
        "summary": {
            "total": 0,
            "fixed": 0,
            "unfixed": 0,
            "by_type": {},
            "by_stage": {},
            "verdict": "CLEAN",
            "detail": "No errors found. Code executed cleanly in sandbox.",
        },
    }


def _parse_analyze_request():
    """Validate and extract common inputs for /api/analyze and /api/analyze/stream."""
    data = request.json or {}
    filename = safe_name(data.get('filename'))
    posted = data.get('code')
    explicit_lang = data.get('language')
    if isinstance(posted, str):
        code = posted
    elif filename:
        code = read_source(filename)
    else:
        return None, (jsonify({"error": "File not found"}), 404)
    if len(code.encode("utf-8", "ignore")) > MAX_CODE_BYTES:
        return None, (jsonify({"error": "Input too large"}), 413)

    lang = detect_language(filename=filename or data.get('filename'), code=code, explicit=explicit_lang)
    max_iters = min(max(int(data.get('max_iterations', 15)), 1), 30)
    use_llm = bool(data.get('use_llm', False))
    want_stream = bool(data.get('stream')) or ('text/event-stream' in (request.headers.get('Accept') or ''))
    return {
        "code": code,
        "filename": filename or data.get('filename'),
        "lang": lang,
        "max_iters": max_iters,
        "use_llm": use_llm,
        "want_stream": want_stream,
    }, None


def _stream_agentic_analyze(req_info):
    """Run AgenticCompilerCoordinator.compile_and_harden() in a worker thread and stream SSE events."""
    t_req = time.perf_counter()
    code = req_info["code"]
    lang = req_info["lang"]
    max_iters = req_info["max_iters"]
    use_llm = req_info["use_llm"]
    ev_queue = queue.Queue()

    def on_event(ev):
        ev_queue.put(ev)

    def worker():
        try:
            vulns, sec_log, blocked, audit_rep = _scan_with_report(code, language=lang)
            sec_struct = [
                {
                    "line": v["line"],
                    "severity": v["severity"],
                    "type": v["type"],
                    "metric_id": v.get("metric_id", ""),
                    "cwe": v.get("cwe", ""),
                    "message": v["message"],
                }
                for v in vulns
            ]
            coordinator = AgenticCompilerCoordinator(
                max_iterations=1 if blocked else max_iters,
                use_llm=use_llm,
            )
            coord_res = coordinator.compile_and_harden(
                code,
                language=lang,
                execute_sandbox=not blocked,
                on_event=on_event,
                initial_audit=audit_rep,
            )
            payload = _build_agentic_analyze_payload(
                code, lang, coord_res, vulns, sec_struct, sec_log, blocked, t_req
            )
            ev_queue.put({"type": "result", "data": payload})
        except CompilerNotFound as exc:
            ev_queue.put({"type": "error", "data": {"status": "error", "error": str(exc)}})
        except Exception as exc:
            ev_queue.put({"type": "error", "data": {"status": "error", "error": f"Agentic compiler error: {exc}"}})
        finally:
            ev_queue.put(None)

    threading.Thread(target=worker, daemon=True).start()

    def generate():
        yield _format_sse("start", {
            "language": lang,
            "loc": len(code.splitlines()),
            "filename": req_info["filename"] or "",
            "max_iterations": max_iters,
        })
        while True:
            item = ev_queue.get()
            if item is None:
                break
            yield _format_sse(item["type"], item["data"])

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    req_info, err_resp = _parse_analyze_request()
    if err_resp is not None:
        return err_resp

    if req_info["want_stream"]:
        return _stream_agentic_analyze(req_info)

    t_req = time.perf_counter()
    code = req_info["code"]
    lang = req_info["lang"]
    vulns, sec_log, blocked, audit_rep = _scan_with_report(code, language=lang)
    sec_struct = [
        {
            "line": v["line"],
            "severity": v["severity"],
            "type": v["type"],
            "metric_id": v.get("metric_id", ""),
            "cwe": v.get("cwe", ""),
            "message": v["message"],
        }
        for v in vulns
    ]
    try:
        coordinator = AgenticCompilerCoordinator(
            max_iterations=1 if blocked else req_info["max_iters"],
            use_llm=req_info["use_llm"],
        )
        coord_res = coordinator.compile_and_harden(
            code, language=lang, execute_sandbox=not blocked, initial_audit=audit_rep
        )
    except CompilerNotFound as e:
        return jsonify({"status": "error", "error": str(e)}), 503
    except RuntimeError as e:
        return jsonify({"status": "error", "error": f"Sandbox failure: {e}"}), 500

    payload = _build_agentic_analyze_payload(
        code, lang, coord_res, vulns, sec_struct, sec_log, blocked, t_req
    )
    return jsonify(payload)


@app.route('/api/analyze/stream', methods=['POST'])
def analyze_code_stream():
    """Dedicated Server-Sent Events (SSE) endpoint streaming real-time 5-agent messages."""
    req_info, err_resp = _parse_analyze_request()
    if err_resp is not None:
        return err_resp
    return _stream_agentic_analyze(req_info)


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


@app.route('/suite-report')
def suite_report_page():
    return render_template('suite_report.html')


@app.route('/api/suite-report', methods=['GET'])
def api_suite_report():
    """Returns the precomputed or live comprehensive test-suite report separating
    Normal Error Diagnosis Test Files from Security Test Files."""
    report_path = os.path.join("report_assets", "comprehensive_suite_report.json")
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                return jsonify(json.load(f))
        except Exception:
            pass
    return jsonify({"error": "Report not yet generated"}), 404


@app.route('/api/security-metrics', methods=['POST'])
def api_security_metrics():
    """Run the 52-metric AST/static security engine on submitted source code."""
    data = request.json or {}
    code = data.get('code', '')
    filename = data.get('filename')
    if not code and filename:
        safe = safe_name(filename)
        if not safe:
            return jsonify({"error": "Invalid filename"}), 400
        code = read_source(safe)
    if not isinstance(code, str) or not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code.encode("utf-8", "ignore")) > 2_000_000:
        return jsonify({"error": "Code exceeds 2 MB limit"}), 413

    language = detect_language(filename=filename, code=code, explicit=data.get('language'))
    report = SecurityMetricsEngine().analyze(code, language=language)
    return jsonify(report)


@app.route('/api/agentic-compile', methods=['POST'])
def api_agentic_compile():
    """Run the 5-agent Secure Agentic AI Compiler pipeline on submitted source code."""
    data = request.json or {}
    code = data.get('code', '')
    filename = data.get('filename')
    if not code and filename:
        safe = safe_name(filename)
        if not safe:
            return jsonify({"error": "Invalid filename"}), 400
        code = read_source(safe)
    if not isinstance(code, str) or not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code.encode("utf-8", "ignore")) > 2_000_000:
        return jsonify({"error": "Code exceeds 2 MB limit"}), 413

    language = detect_language(filename=filename, code=code, explicit=data.get('language'))
    max_iters = min(max(int(data.get('max_iterations', 5)), 1), 15)
    execute_sandbox = bool(data.get('execute_sandbox', True))
    use_llm = bool(data.get('use_llm', False))

    coordinator = AgenticCompilerCoordinator(max_iterations=max_iters, use_llm=use_llm)
    result = coordinator.compile_and_harden(code, language=language, execute_sandbox=execute_sandbox)
    return jsonify(result)


@app.route('/api/apply-patch', methods=['POST'])
def api_apply_patch():
    """Apply a single diagnostic issue patch using LibCST (Concrete Syntax Tree)
    instead of fragile string slicing or indentation guessing."""
    data = request.json or {}
    code = data.get('code')
    issue = data.get('issue')
    if not isinstance(code, str):
        return jsonify({"error": "Code must be text"}), 400
    if not isinstance(issue, dict):
        return jsonify({"error": "Missing issue payload"}), 400
    if len(code.encode("utf-8", "ignore")) > MAX_CODE_BYTES:
        return jsonify({"error": "Input too large"}), 413

    lang = detect_language(
        filename=data.get('filename'),
        code=code,
        explicit=data.get('language'),
    )
    res = apply_single_issue_patch_cst(code, issue, language=lang)
    return jsonify(res)


@app.route('/api/sandbox/status', methods=['GET'])
def sandbox_status():
    """Inspect the active sandbox engine, isolation boundaries, and capabilities."""
    return jsonify(get_sandbox_status())


if __name__ == '__main__':
    import socket

    def find_available_port(default_port=5001):
        if "PORT" in os.environ:
            return int(os.environ["PORT"])
        for p in [default_port, 5003, 5004, 5005]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', p))
                    return p
            except OSError:
                continue
        return default_port

    port = find_available_port(5001)
    print("\n" + "="*60)
    print(f"[TOACD Studio Initiated]")
    print(f"Server is running at: http://127.0.0.1:{port}")
    if port != 5001:
        print(f"(Note: Port 5001 is in use by another process; using port {port})")
    print("="*60 + "\n")

    # debug=False: Flask's debugger lets anyone who reaches the page run code on your machine.
    app.run(host='127.0.0.1', debug=False, port=port, use_reloader=False, threaded=True)
