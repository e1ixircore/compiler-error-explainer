# run_checks.py - runs every sample through the REAL pipeline and prints a verdict table.
# verify_fix() re-analyzes + re-executes each patch, so this measures "does the fix
# work", not "does the text resemble a template" (the weakness of evaluation.py).
import time
from app import repair_loop, verify_fix, scan
from error_extractor import extract_error

cases = [(f, open(f, encoding="utf-8").read()) for f in
         ["test1.py", "test2.py", "test3.py", "test4.py", "test5.py", "test6.py", "test7.py",
          "test8.py", "test_case_large.py", "test_security.py", "test9.py"]]
cases.append(("nested(20k)", "x = " + "+".join(["1"] * 20000)))            # nesting stress
cases.append(("from-os-import", "from os import system\nsystem('echo hi')"))  # bypass check

print(f"{'case':20}{'detected':20}{'verdict':18}{'sec'}")
for label, code in cases:
    if scan(code)[2]:
        print(f"{label:20}{'-':20}{'BLOCKED (security)':18}"); continue
    t = time.perf_counter()
    err = extract_error(code).get("error_type")
    fixed, _ = repair_loop(code)
    verdict = verify_fix(code, fixed)["verdict"]
    print(f"{label:20}{str(err):20}{verdict:18}{time.perf_counter()-t:.2f}")