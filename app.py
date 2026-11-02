from collections import Counter
import difflib
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

# CRITICAL/HIGH findings mean "do not execute, do not save".
BLOCKING = {"CRITICAL", "HIGH"}
MAX_REPAIR_PASSES = 25     # hard cap on patch passes (each pass fixes ONE error)
MAX_REPAIR_SECONDS = 20    # wall-clock budget: every runtime pass spawns a sandbox, so bound the total
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
    files = glob.glob("test*.py")
    fixed_files = glob.glob("*_fixed.py")
    all_files = sorted(set(files + fixed_files))
    all_files = [f for f in all_files
                 if f not in ["test_ir.py", "test_nlp.py", "sample_input.py", "sample_input_fixed.py"]]
    return [{"filename": f, "is_fixed": "_fixed.py" in f} for f in all_files]


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


def scan(code):
    """Returns (vulns, formatted log lines, is_blocked)."""
    vulns = SecurityAnalyzer().scan_code(code)
    log = [f"[{v['severity']}] Line {v['line']}: {v['message']}" for v in vulns]
    return vulns, log, any(v["severity"] in BLOCKING for v in vulns)


def fix_is_safe(original, fixed):
    """A patch may never ADD a vulnerability class that the original didn't have."""
    sa = SecurityAnalyzer()
    before = Counter(v["type"] for v in sa.scan_code(original))
    after = Counter(v["type"] for v in sa.scan_code(fixed))
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

def _changed_lines(before, after):
    """(sign, text) pairs for lines a patch removed ('-') or added ('+'), for display."""
    diff = list(difflib.unified_diff(before.split("\n"), after.split("\n"), lineterm="", n=0))
    return [(l[0], l[1:].strip()) for l in diff[2:] if not l.startswith("@@")]


def repair_loop(code, max_iters=MAX_REPAIR_PASSES, time_budget=MAX_REPAIR_SECONDS, first_ir=None):
    """Agent loop: perceive (analyze) -> decide (pick rule) -> act (patch) -> observe (re-analyze).
    Runs UNTIL THE CODE IS CLEAN, one error per pass, so any number of errors can be fixed.
    Termination is guaranteed by four independent stops (a loop that 'continues until done'
    must prove it cannot spin forever):
      1. clean           : no error remains                       -> success
      2. no safe fix     : no rule, or the patch fails safety     -> stuck
      3. no progress     : patch reproduces an earlier program, or the same error recurs 3x
      4. budget          : pass cap or wall-clock limit reached   -> partial
    first_ir lets the caller hand over an analysis it already ran (avoids executing twice)."""
    history, current = [], code
    seen_states = {code}                 # every program version produced so far (cycle detection)
    repeats = Counter()                  # how often the same (type, message, line) came back
    t_start = time.perf_counter()
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
        if ir_dict["error_type"] == "SyntaxError":
            stage = "parser"             # rejected before any AST existed
        err = CompilerError(ir_dict["error_type"], ir_dict.get("error_message"),
                            ir_dict.get("line_number"), stage, tb)
        ir = json.loads(IRGenerator(current, err).generate_ir())   # the IR: one JSON payload PER error
        ir["suggestion"] = ir_dict.get("suggestion")          # symbol-table "did you mean"
        # Promised fields for the Diagnostic JSON (now attached to every issue, not just the first).
        ir["phase"] = stage                                   # "parser" | "static" | "runtime"
        ir["column"] = ir_dict.get("column")                  # only the static checker knows columns

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
        entry = {"step": i + 1, "error": ir["error_type"], "line": ln, "column": ir["column"],
                 "stage": stage, "source": src, "ir": ir, "trace": frames,
                 "explanation": explanation, "explain_ms": explain_ms, "patch": []}

        sig = (ir["error_type"], ir.get("error_message"), ln)
        repeats[sig] += 1
        fixed = explainer.generate_fixed_code(ir, current)    # decide + act
        if fixed == current or not fix_is_safe(current, fixed):
            entry["result"] = "stuck (no safe fix)"
            history.append(entry)
            break
        if fixed in seen_states or repeats[sig] >= 3:         # patching in circles
            entry["result"] = "stuck (patch is not making progress)"
            history.append(entry)
            break
        seen_states.add(fixed)
        entry["patch"] = _changed_lines(current, fixed)
        entry["result"] = "patched"
        history.append(entry)
        current = fixed                                       # observe on next iteration
    else:
        history.append({"step": "final",
                        "result": f"stopped: reached the {max_iters}-pass safety cap; errors may remain"})
    return current, history


STAGE_LABEL = {"parser": "the parser", "static": "static analysis", "runtime": "runtime execution"}


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
    data = request.json or {}
    filename = safe_name(data.get('filename'))
    if not filename:
        return jsonify({"error": "File not found"}), 404

    code = read_source(filename)
    if len(code.encode("utf-8", "ignore")) > MAX_CODE_BYTES:
        return jsonify({"error": "Input too large"}), 413

    # ---- STAGE 0: security gate. Runs BEFORE anything executes. ----
    vulns, sec_log, blocked = scan(code)
    if blocked:
        return jsonify({
            "status": "blocked",
            "original_code": code,
            "raw_text": "[SECURITY] Execution BLOCKED. Critical/High findings:\n  " + "\n  ".join(sec_log),
            "metrics": "Not executed (blocked by security scan).",
        })

    # ---- STAGES 1-3: static analysis, then sandboxed run (inside extract_error) ----
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

        log_text = format_pipeline(sec_log, ir_dict, repair_history, verdict)
        log_text += "\n" + format_diagnosis(repair_history)
        total_explain = sum(h.get("explain_ms", 0) for h in repair_history)
        log_text += f"\n[PERFORMANCE] Explanation time: {total_explain:.3f} ms total\n"
        log_text += "\n[FIX VERIFICATION] (patch re-analyzed and re-executed in sandbox)\n"
        log_text += f"Verdict : {verdict['verdict']}\n"
        log_text += f"Detail  : {verdict['detail']}\n"

        return jsonify({
            "status": "error_intercepted",
            "original_code": code,
            "raw_text": log_text,
            "diagnostics": [h["ir"] for h in repair_history if h.get("error")],   # full IR JSON, one per issue
            "fixed_code": fixed_code,
            "metrics": build_metrics(ir_dict),
        })

    # No error found
    out_msg = "Execution completed normally. No compilation or runtime errors intercepted."
    captured = (ir_dict or {}).get("stdout", "")
    if captured and captured.strip():
        out_msg += f"\n\n[STDOUT OUTPUT]:\n{captured.strip()}"
    return jsonify({
        "status": "success",
        "original_code": code,
        "message": out_msg,
        "fixed_code": code,
        "security_alerts": sec_log,
        "metrics": build_metrics(ir_dict),
    })


@app.route('/api/execute', methods=['POST'])
def execute_code():
    code_to_run = (request.json or {}).get('code', '')
    if len(code_to_run.encode("utf-8", "ignore")) > MAX_CODE_BYTES:
        return jsonify({"output": "BLOCKED: input too large."})
    _, _, blocked = scan(code_to_run)
    if blocked:
        return jsonify({"output": "BLOCKED: critical security findings, code not executed."})

    try:
        execution = run_code(code_to_run)     # child process + 5s timeout
    except RuntimeError as e:
        return jsonify({"output": f"Sandbox failure: {e}"})

    output = execution["stdout"]
    if execution["error_type"]:
        output += (f"\nCRASH DURING EXECUTION:\n"
                   f"{execution['error_type']}: {execution['error_message']}")
    elif not output.strip():
        output = "Code executed cleanly (No standard output returned)."
    return jsonify({"output": output})


@app.route('/api/save', methods=['POST'])
def save_file():
    data = request.json or {}
    original_filename = safe_name(data.get('filename'))   # must be an existing whitelisted file
    code = data.get('code')

    if not original_filename or not code:
        return jsonify({"error": "Missing or invalid filename/code"}), 400
    if len(code.encode("utf-8", "ignore")) > MAX_CODE_BYTES:
        return jsonify({"error": "Input too large"}), 413
    # Never persist code with critical findings.
    if scan(code)[2]:
        return jsonify({"error": "Refusing to save code with critical security findings"}), 400

    # Always write to <name>_fixed.py so the original test file is never overwritten.
    new_filename = (original_filename if original_filename.endswith("_fixed.py")
                    else original_filename.replace(".py", "_fixed.py"))

    with open(new_filename, "w", encoding="utf-8") as f:
        f.write(code)
    return jsonify({"status": "success", "new_filename": new_filename})


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    import random
    files = glob.glob("test*.py")
    categories = {"Small": [], "Medium": [], "Large": []}

    for f_path in files:
        try:
            with open(f_path, "r", encoding="utf-8", errors="ignore") as f:
                line_count = len(f.readlines())
                if line_count < 50:
                    categories["Small"].append(line_count)
                elif line_count <= 150:
                    categories["Medium"].append(line_count)
                else:
                    categories["Large"].append(line_count)
        except Exception:
            pass

    s_avg = sum(categories["Small"]) / len(categories["Small"]) if categories["Small"] else 20
    m_avg = sum(categories["Medium"]) / len(categories["Medium"]) if categories["Medium"] else 120
    l_avg = sum(categories["Large"]) / len(categories["Large"]) if categories["Large"] else 350
    m_avg = max(m_avg, s_avg + 30)
    l_avg = max(l_avg, m_avg + 100)

    counts = {"Small": s_avg, "Medium": m_avg, "Large": l_avg}
    keys = ["Small", "Medium", "Large"]

    # NOTE: this dashboard is still SYNTHETIC (formulas + random). Label it as such in
    # the UI/report until it's replaced with real benchmark results.
    return jsonify({
        "labels": ["Small Code (<50 lines)", "Medium Code (50-150)", "Large Code (>150)"],
        "responseTime": [counts[k] * 1.5 + random.uniform(2, 5) for k in keys],
        "emissions": [counts[k] * 0.02 + 0.1 for k in keys],
        "raplEnergy": [counts[k] * 0.4 + 2 for k in keys],
        "pinpointOvhd": [counts[k] * 0.0001 + 0.002 for k in keys],
        "energyVirt": [max(85, 99.2 - (counts[k] * 0.03)) for k in keys],
        "modelPerformance": [max(0.7, 0.98 - (counts[k] * 0.0006)) for k in keys],
        "securityRisks": [max(1, int(counts[k] * 0.02)) for k in keys],
        "securityHealing": [max(75, 99 - (counts[k] * 0.05)) for k in keys],
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Saves an uploaded/pasted .py file as test_upload_<name>.py. Does NOT run it.
    The prefix means (a) the existing whitelist lists it automatically and
    (b) an upload can never overwrite one of your real test files."""
    data = request.json or {}
    name = os.path.basename(data.get('filename') or 'pasted.py')   # strips any ../
    code = data.get('code')

    if not isinstance(code, str) or not code.strip():
        return jsonify({"error": "Empty file"}), 400
    if not name.endswith('.py'):
        return jsonify({"error": "Only .py files are accepted"}), 400
    if "\x00" in code:
        return jsonify({"error": "Null byte in source"}), 400      # ast.parse would raise ValueError
    if len(code.encode("utf-8", "ignore")) > MAX_CODE_BYTES:
        return jsonify({"error": "File too large (100 KB max)"}), 413

    # Whitelist characters in the stem so the name can't contain path tricks.
    stem = re.sub(r'[^A-Za-z0-9_]', '_', name[:-3])[:40] or 'file'
    new_name = f"test_upload_{stem}.py"
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