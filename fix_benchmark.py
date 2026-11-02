# fix_benchmark.py
# Measures what actually matters for a compiler-error tool:
#   1. Did it detect the RIGHT error?                      (detection accuracy)
#   2. Did the auto-fix WORK when re-analysed + re-run?    (verify_fix verdict)
#   3. How long / how much energy did it take?            (measured latency, estimated energy)
# It reuses app.py's real functions, so the numbers describe the code you demo.
#
# Run from the project folder:  python fix_benchmark.py
import csv
import os
import statistics
import time

from app import repair_loop, verify_fix, fix_is_safe, read_source
from error_extractor import extract_error

REPEATS = 3   # repeat each file; we report the MEDIAN so one slow run doesn't skew it

# Ground truth = the error each test file was DESIGNED to contain (first one hit).
GROUND_TRUTH = {
    "test1.py": "ZeroDivisionError",
    "test2.py": "SyntaxError",
    "test3.py": "NameError",
    "test4.py": "IndexError",
    "test6.py": "KeyError",
    "test7.py": "TypeError",
    "test8.py": "ModuleNotFoundError",
    "test10.py": "TypeError",          # multi-error file: first error is the TypeError
    "test11.py": "NameError",          # 12-error stress test: first error is a NameError typo
    "test_case_large.py": "NameError",
}

# Mean package power from your powermetrics_log.txt samples (about 4.7 W).
# Energy = power x time. This is an ESTIMATE (the log was not captured during this run);
# say so in the report. Override with:  PKG_POWER_W=5.0 python fix_benchmark.py
PKG_POWER_W = float(os.environ.get("PKG_POWER_W", "4.7"))


def timed(fn, *args):
    t0 = time.perf_counter()
    out = fn(*args)
    return out, (time.perf_counter() - t0) * 1000   # ms


def bench_file(name):
    code = read_source(name)
    t_detect, t_repair, t_verify = [], [], []
    for _ in range(REPEATS):
        ir, d = timed(extract_error, code)                 # stage 1-3: detect
        (fixed, history), r = timed(repair_loop, code)     # agent loop: patch + re-check
        if not fix_is_safe(code, fixed):                   # same final gate as /api/analyze
            fixed = code
        verdict, v = timed(verify_fix, code, fixed)        # closed-loop verification
        t_detect.append(d); t_repair.append(r); t_verify.append(v)

    tb = ir.get("traceback") or ""
    patches = sum(1 for h in history if h.get("result") == "patched")
    total_ms = statistics.median(t_detect) + statistics.median(t_repair) + statistics.median(t_verify)
    return {
        "file": name,
        "truth": GROUND_TRUTH.get(name, "?"),
        "detected": ir.get("error_type"),
        "stage": "static" if tb.startswith("(static") else "runtime",
        "patches": patches,
        "verdict": verdict["verdict"],
        "detail": verdict["detail"],
        "detect_ms": round(statistics.median(t_detect), 2),
        "repair_ms": round(statistics.median(t_repair), 2),
        "verify_ms": round(statistics.median(t_verify), 2),
        "total_ms": round(total_ms, 2),
        "est_energy_mJ": round(PKG_POWER_W * total_ms, 2),   # W x ms = mJ
    }


def main():
    rows = [bench_file(f) for f in GROUND_TRUTH if os.path.exists(f)]
    if not rows:
        print("No test files found. Run from the project folder.")
        return

    print("\n" + "=" * 112)
    print(f"{'file':<20}{'truth':<20}{'detected':<20}{'stage':<9}{'patches':>8}  {'verdict':<10}"
          f"{'detect':>8}{'repair':>8}{'verify':>8}{'mJ':>8}")
    print("-" * 112)
    for r in rows:
        ok = "" if r["detected"] == r["truth"] else "  <-- mismatch"
        print(f"{r['file']:<20}{r['truth']:<20}{str(r['detected']):<20}{r['stage']:<9}{r['patches']:>8}  "
              f"{r['verdict']:<10}{r['detect_ms']:>8}{r['repair_ms']:>8}{r['verify_ms']:>8}"
              f"{r['est_energy_mJ']:>8}{ok}")
    print("=" * 112)

    n = len(rows)
    correct = sum(r["detected"] == r["truth"] for r in rows)
    verified = sum(r["verdict"] == "VERIFIED" for r in rows)
    print(f"Detection accuracy : {correct}/{n}")
    print(f"Fix success rate   : {verified}/{n} VERIFIED "
          f"(PARTIAL={sum(r['verdict'] == 'PARTIAL' for r in rows)}, "
          f"REJECTED={sum(r['verdict'] == 'REJECTED' for r in rows)}, "
          f"NO FIX={sum(r['verdict'] == 'NO FIX GENERATED' for r in rows)})")
    print(f"Median total time  : {statistics.median(r['total_ms'] for r in rows):.1f} ms per file "
          f"(~{statistics.median(r['est_energy_mJ'] for r in rows):.0f} mJ estimated at {PKG_POWER_W} W)")

    # Green IT insight: static detection never launches a subprocess, runtime detection does.
    for stage in ("static", "runtime"):
        d = [r["detect_ms"] for r in rows if r["stage"] == stage]
        if d:
            print(f"Detection latency, {stage:<7}: median {statistics.median(d):.2f} ms over {len(d)} file(s)")

    with open("fix_benchmark_results.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("Saved fix_benchmark_results.csv")


if __name__ == "__main__":
    main()