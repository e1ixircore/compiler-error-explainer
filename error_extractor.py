import json
import subprocess
import sys
from static_analyzer import static_check
import os

try:
    from codecarbon import EmissionsTracker
    CODECARBON_AVAILABLE = True
except ImportError:
    CODECARBON_AVAILABLE = False


_EXECUTION_RUNNER = """
import contextlib
import io
import json
import sys
import time
import traceback

code = sys.stdin.read()
captured = io.StringIO()
result = {
    "error_type": None,
    "error_message": None,
    "line_number": None,
    "traceback": None,
    "stdout": "",
}
start = time.perf_counter()
try:
    compiled = compile(code, "<string>", "exec")
    with contextlib.redirect_stdout(captured):
        exec(compiled, {"__name__": "__main__"})
except BaseException as error:
    result["error_type"] = type(error).__name__
    result["error_message"] = str(error)
    result["traceback"] = traceback.format_exc()
    if isinstance(error, SyntaxError):
        result["line_number"] = error.lineno
    else:
        for frame in reversed(traceback.extract_tb(sys.exc_info()[2])):
            if frame.filename == "<string>":
                result["line_number"] = frame.lineno
                break
result["stdout"] = captured.getvalue()
result["execution_time_sec"] = time.perf_counter() - start
sys.stdout.write(json.dumps(result))
"""


def run_code(code, timeout=5):
    """Run code in a child process with a hard time limit."""
    try:
        completed = subprocess.run(
            [sys.executable, "-c", _EXECUTION_RUNNER],
            input=code,
            capture_output=True,
            text=True,
            timeout=timeout,
            start_new_session=True,
        )
    except subprocess.TimeoutExpired as error:
        partial_output = error.stdout or ""
        if isinstance(partial_output, bytes):
            partial_output = partial_output.decode("utf-8", errors="replace")
        return {
            "error_type": "TimeoutError",
            "error_message": f"Execution exceeded the {timeout}-second time limit.",
            "line_number": None,
            "traceback": "",
            "stdout": partial_output,
            "execution_time_sec": timeout,
        }

    if completed.returncode != 0:
        raise RuntimeError(
            f"Code execution process exited unexpectedly "
            f"(exit status {completed.returncode}): {completed.stderr.strip()}"
        )
    return json.loads(completed.stdout)


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
        # Unparseable code: static_check can't build an AST. Fall through to
        # run_code(), whose child process reports the SyntaxError with line number.
        static_errors = []
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
        ir["all_errors"] = static_errors   # every error found, not just the first
        ir["green_metrics"] = {"execution_time_sec": 0, "emissions_kg": 0,
                               "energy_consumed_kwh": 0}
        return ir

    tracker = None
    if CODECARBON_AVAILABLE and os.environ.get("USE_CODECARBON") == "1":
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