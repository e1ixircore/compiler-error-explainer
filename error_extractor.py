import json
import subprocess
import sys
from static_analyzer import static_check
import os
from sandbox import run_sandboxed_python, SANDBOX_PYTHON_RUNNER

try:
    from codecarbon import EmissionsTracker
    CODECARBON_AVAILABLE = True
except ImportError:
    CODECARBON_AVAILABLE = False


_EXECUTION_RUNNER = SANDBOX_PYTHON_RUNNER


def classify_stage(ir):
    """Which compiler stage FOUND this error: 'parser' | 'static' | 'runtime'.
    One definition used by app.py, fix_benchmark.py and the dashboard, so they cannot disagree.
    The traceback prefix is written by extract_error itself:
        '(parser: ...'  panic-mode recovery after ast.parse failed (no AST existed)
        '(static ...'   StaticChecker, or the nesting abort (code was not executed)
        anything else   a real traceback from the sandbox (code was executed)
    Syntax/Indentation errors are always parser-stage, whatever the prefix."""
    tb = (ir or {}).get("traceback") or ""
    if tb.startswith("(parser") or (ir or {}).get("error_type") in ("SyntaxError", "IndentationError"):
        return "parser"
    return "static" if tb.startswith("(static") else "runtime"


def run_code(code, timeout=5):
    """Run code in a secure sandbox (macOS Seatbelt / Docker / AuditHook) with a hard time limit."""
    return run_sandboxed_python(code, timeout=timeout)


def extract_error(code):
    """
    Executes Python code in a child process, capturing error type, message, traceback,
    line number, and optionally tracks CodeCarbon emissions.
    
    Returns a dictionary (IR) with the extracted details.
    """
    ir = {
        "error_type": None,
        "error_message": None,
        "line_number": None,
        "traceback": None,
        "green_metrics": None,
        "stdout": ""
    }

    # NEW: static analysis stage. Runs in-process but never executes the code,
    # so nothing dangerous can happen here. Order: static first, sandbox second.
    try:
        static_errors = static_check(code)
    except SyntaxError:
        # PANIC-MODE RECOVERY: the parser gave no AST, so recover and collect ALL syntax errors.
        from panic_recovery import collect_syntax_errors
        errs, _, _ = collect_syntax_errors(code)
        if errs:
            first = errs[0]
            ir.update(error_type=first["error_type"], error_message=first["error_message"],
                      line_number=first["line_number"],
                      traceback="(parser: panic-mode recovery, code was not executed)")
            ir["column"] = first["column"]
            ir["all_errors"] = errs
            ir["green_metrics"] = {"execution_time_sec": 0, "emissions_kg": 0,
                                   "energy_consumed_kwh": 0}
            return ir
        static_errors = []          # recovery found nothing: fall through to the sandbox as before
    except (RecursionError, MemoryError):
        # Nesting protection: a deeply nested input must not crash the compiler itself.
        ir.update(error_type="NestingError",
                  error_message="Input is too deeply nested to analyze safely.",
                  line_number=1,
                  traceback="(static analysis aborted: nesting limit)")
        ir["green_metrics"] = {"execution_time_sec": 0, "emissions_kg": 0,
                               "energy_consumed_kwh": 0}
        return ir

    if static_errors:
        first = static_errors[0]
        ir.update(error_type=first["error_type"],
                  error_message=first["error_message"],
                  line_number=first["line_number"],
                  traceback="(static analysis: code was not executed)")
        ir["column"] = first["column"]
        ir["suggestion"] = first.get("suggestion")   # symbol-table "did you mean"
        ir["all_errors"] = static_errors   # every error found, not just the first
        ir["green_metrics"] = {"execution_time_sec": 0, "emissions_kg": 0,
                               "energy_consumed_kwh": 0}
        return ir

    tracker = None
    if (CODECARBON_AVAILABLE and os.environ.get("USE_CODECARBON") == "1"
            and os.environ.get("CODECARBON_SERVER_LIFETIME") != "1"):
        try:
            # Using log_level error to avoid noisy console outputs
            tracker = EmissionsTracker(save_to_file=True, log_level='error')
            tracker.start()
        except Exception:
            tracker = None

    execution = run_code(code)
    ir.update({
        "error_type": execution["error_type"],
        "error_message": execution["error_message"],
        "line_number": execution["line_number"],
        "traceback": execution["traceback"],
        "stdout": execution["stdout"],
    })
    duration = execution["execution_time_sec"]

    # Record Green metrics
    if tracker:
        try:
            emissions = tracker.stop()
            ir["green_metrics"] = {
                "emissions_kg": emissions,
                "energy_consumed_kwh": tracker.final_emissions_data.energy_consumed if emissions else 0,
                "execution_time_sec": duration
            }
        except Exception:
            ir["green_metrics"] = {
                "execution_time_sec": duration,
                "emissions_kg": 0,
                "energy_consumed_kwh": 0
            }
    else:
        ir["green_metrics"] = {
            "execution_time_sec": duration,
            "emissions_kg": 0,
            "energy_consumed_kwh": 0
        }

    return ir