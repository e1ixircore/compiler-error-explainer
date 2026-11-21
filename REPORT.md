# IntelliFix — Comprehensive Error Diagnosis & Security Test Suite Report

## 1. Executive Summary & Pipeline Architecture

IntelliFix follows a strict, beginner-friendly compiler pipeline:
1. **Stage 1 — Security Gate First (0–40 pts)**: Scans source code against **52 security metrics** (`SEC_01`–`SEC_52`). If any **CRITICAL** or **HIGH** vulnerability is detected, the compiler **stops immediately** (`Grade F · 0/100`), does not run static or runtime error analysis, and offers an Agentic AI Security Sanitization patch (plus an inline code editor) so the user can either resolve the threat or stop diagnosis.
2. **Stage 2 — Static, Runtime & Logical Error Discovery + Agentic AI Patching (0–45 pts)**: Once the Security Gate passes, the compiler discovers all syntax, static symbol-table, logical AST, and sandboxed runtime errors. Each error is presented in a beginner-friendly diagnostic card (**What went wrong / Why it happened / How to fix**) with:
   - **One-Click Agentic AI Fix** for unambiguous fixable errors (**90.7%** of all errors).
   - **Interactive Inline Code Box** (no `<textarea>`) for manual patching on both ambiguous errors (**9.3%**) and custom edits.
3. **Stage 3 — Code Efficiency & Execution Quality (0–15 pts)**: Evaluated once the program is clean and executable, measuring AST cyclomatic complexity, loop nesting depth, and sandbox runtime.

---

## 2. Corpus Overview (Separated Error Suites vs. Security Suites)

| Metric | Value | Notes |
| :--- | :---: | :--- |
| **Total Test Files Evaluated** | **85 files** | **135,679 total lines of code** (58 files >= 2,000 LOC) |
| **1. Normal Error Diagnosis Test Files** | **60 files** | 19 Standard Root Files + 41 Large Benchmarks (>= 2,000 LOC, **0 security blocks**) |
| **Total Compiler/Runtime/Logical Errors** | **484 errors** | Distributed across all 60 normal error test files |
| **Unambiguous Auto-Fixable Errors** | **439 (90.7%)** | Automatically patched and verified by the Agentic AI Compiler |
| **Occasional Ambiguous Errors** | **45 (9.3%)** | Flagged for developer judgment via the interactive inline code box |
| **2. Dedicated Security Guardrail Files** | **25 files** | 7 Standard Security Traps + 18 Large Security Benchmarks (>= 2,000 LOC) |
| **Total Security Findings Intercepted** | **91 findings** | Intercepted at Stage 1 across the 52-metric security engine |

---

## 3. Error Breakdown by Type & Stage (Across the 59 Normal Error Files)

### 3A. Errors by Compiler Stage
| Compiler Stage | Error Count | Share |
| :--- | :---: | :---: |
| **STATIC** | 400 | 82.6% |
| **COMPILER** | 41 | 8.5% |
| **RUNTIME** | 38 | 7.9% |
| **PARSER** | 5 | 1.0% |

### 3B. Errors by Type
| Error Type | Count | Category |
| :--- | :---: | :--- |
| `NameError` | **74** | Compiler / Runtime / Logical Diagnostic |
| `LogicalError` | **61** | Compiler / Runtime / Logical Diagnostic |
| `TypeError` | **60** | Compiler / Runtime / Logical Diagnostic |
| `ValueError` | **60** | Compiler / Runtime / Logical Diagnostic |
| `IndexError` | **56** | Compiler / Runtime / Logical Diagnostic |
| `ZeroDivisionError` | **47** | Compiler / Runtime / Logical Diagnostic |
| `AttributeError` | **43** | Compiler / Runtime / Logical Diagnostic |
| `KeyError` | **33** | Compiler / Runtime / Logical Diagnostic |
| `MissingStdPrefix` | **12** | Compiler / Runtime / Logical Diagnostic |
| `UndeclaredIdentifier` | **7** | Compiler / Runtime / Logical Diagnostic |
| `MissingSemicolon` | **6** | Compiler / Runtime / Logical Diagnostic |
| `SyntaxError` | **5** | Compiler / Runtime / Logical Diagnostic |
| `AssignmentInCondition` | **4** | Compiler / Runtime / Logical Diagnostic |
| `CompileError` | **4** | Compiler / Runtime / Logical Diagnostic |
| `ModuleNotFoundError` | **3** | Compiler / Runtime / Logical Diagnostic |
| `TypeMismatch` | **2** | Compiler / Runtime / Logical Diagnostic |
| `TimeoutError` | **1** | Compiler / Runtime / Logical Diagnostic |
| `MissingInclude` | **1** | Compiler / Runtime / Logical Diagnostic |
| `MissingHeaderFile` | **1** | Compiler / Runtime / Logical Diagnostic |
| `DivisionByZero` | **1** | Compiler / Runtime / Logical Diagnostic |
| `ArrayOutOfBounds` | **1** | Compiler / Runtime / Logical Diagnostic |
| `InvalidMainSignature` | **1** | Compiler / Runtime / Logical Diagnostic |
| `WrongStreamOperator` | **1** | Compiler / Runtime / Logical Diagnostic |

---

## 4. Suite 1A — Standard Normal Error Test Files (19 Files, 0 Security Blocks)

| File | Lang | LOC | Initial Score | Projected Score | Total Errors | Fixable | Ambiguous | Error Details |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `test1.py` | PYTHON | 43 | 65/100 (C) | 100/100 (A) | **4** | 4 | 0 | L19:LogicalError(fixable/static), L25:TypeError(fixable/static), L31:NameError(fixable/static), L39:ZeroDivisionError(fixable/static) |
| `test2.py` | PYTHON | 28 | 57/100 (D) | 100/100 (A) | **4** | 4 | 0 | L6:SyntaxError(fixable/parser), L10:SyntaxError(fixable/parser), L19:IndexError(fixable/static), L17:TypeError(fixable/runtime) |
| `test3.py` | PYTHON | 38 | 60/100 (C) | 78/100 (B) | **5** | 4 | 1 | L7:NameError(fixable/static), L12:KeyError(fixable/static), L17:AttributeError(fixable/static), L22:ZeroDivisionError(fixable/static), L29:NameError(ambiguous/static) |
| `test4.py` | PYTHON | 32 | 63/100 (C) | 100/100 (A) | **4** | 4 | 0 | L7:IndexError(fixable/static), L13:TypeError(fixable/static), L17:ValueError(fixable/static), L22:LogicalError(fixable/static) |
| `test5.py` | PYTHON | 13 | 59/100 (D) | 100/100 (A) | **3** | 3 | 0 | L5:NameError(fixable/static), L7:NameError(fixable/static), L9:TypeError(fixable/static) |
| `test6.py` | PYTHON | 33 | 61/100 (C) | 80/100 (B) | **5** | 4 | 1 | L5:KeyError(fixable/static), L7:NameError(fixable/static), L11:TypeError(fixable/static), L15:LogicalError(fixable/static), L22:LogicalError(ambiguous/static) |
| `test7.py` | PYTHON | 35 | 57/100 (D) | 100/100 (A) | **5** | 5 | 0 | L6:SyntaxError(fixable/parser), L12:TypeError(fixable/static), L18:IndexError(fixable/static), L20:NameError(fixable/static), L26:ZeroDivisionError(fixable/runtime) |
| `test8.py` | PYTHON | 30 | 61/100 (C) | 77/100 (B) | **4** | 3 | 1 | L3:ModuleNotFoundError(fixable/static), L6:ModuleNotFoundError(ambiguous/static), L11:NameError(fixable/static), L22:KeyError(fixable/static) |
| `testA.py` | PYTHON | 2 | 65/100 (C) | — | **1** | 0 | 1 | LNone:TimeoutError(ambiguous/runtime) |
| `testB.py` | PYTHON | 10 | 57/100 (D) | 100/100 (A) | **3** | 3 | 0 | L5:TypeError(fixable/static), L6:NameError(fixable/static), L7:KeyError(fixable/static) |
| `testC.py` | PYTHON | 21 | 43/100 (D) | 100/100 (A) | **12** | 12 | 0 | L7:NameError(fixable/static), L8:NameError(fixable/static), L9:NameError(fixable/static), L10:TypeError(fixable/static), L11:TypeError(fixable/static), L12:TypeError(fixable/static), L13:ZeroDivisionError(fixable/static), L14:ZeroDivisionError(fixable/static), L15:IndexError(fixable/static), L16:IndexError(fixable/static), L17:KeyError(fixable/static), L18:KeyError(fixable/static) |
| `testD.py` | PYTHON | 10 | 53/100 (D) | 100/100 (A) | **4** | 4 | 0 | L6:NameError(fixable/static), L6:NameError(fixable/static), L7:TypeError(fixable/static), L8:ZeroDivisionError(fixable/static) |
| `testE.py` | PYTHON | 556 | 76/100 (B) | 83/100 (B) | **4** | 3 | 1 | L18:SyntaxError(fixable/parser), L23:SyntaxError(fixable/parser), L27:NameError(ambiguous/static), L31:IndexError(fixable/static) |
| `testF.py` | PYTHON | 502 | 79/100 (B) | 83/100 (B) | **3** | 2 | 1 | L22:IndexError(fixable/static), L25:KeyError(fixable/static), L28:ModuleNotFoundError(ambiguous/static) |
| `testG.py` | PYTHON | 7 | 73/100 (C) | 100/100 (A) | **1** | 1 | 0 | L3:ValueError(fixable/static) |
| `test_case_large.py` | PYTHON | 241 | 58/100 (D) | — | **1** | 0 | 1 | L237:NameError(ambiguous/static) |
| `test_case_new.py` | PYTHON | 45 | 62/100 (C) | 80/100 (B) | **5** | 4 | 1 | L13:TypeError(fixable/static), L18:IndexError(fixable/static), L23:KeyError(fixable/static), L28:NameError(fixable/static), L32:LogicalError(ambiguous/static) |
| `test_cpp_basics.cpp` | CPP | 562 | 76/100 (B) | 98/100 (A) | **5** | 5 | 0 | L559:MissingSemicolon(fixable/compiler), L560:MissingInclude(fixable/compiler), L560:MissingStdPrefix(fixable/compiler), L560:UndeclaredIdentifier(fixable/compiler), L560:MissingStdPrefix(fixable/compiler) |
| `test_cpp_bugs.cpp` | CPP | 612 | 71/100 (C) | 77/100 (B) | **9** | 4 | 5 | L14:MissingHeaderFile(fixable/compiler), L569:TypeMismatch(ambiguous/compiler), L578:DivisionByZero(ambiguous/compiler), L583:ArrayOutOfBounds(ambiguous/compiler), L587:TypeMismatch(ambiguous/compiler), L592:AssignmentInCondition(fixable/compiler), L599:UndeclaredIdentifier(ambiguous/compiler), L602:InvalidMainSignature(fixable/compiler), L604:WrongStreamOperator(fixable/compiler) |

---

## 5. Suite 1B — 2,000+ Line Large-Scale Error Diagnosis Benchmarks (40 Files, 0 Security Blocks)

| File | Lang | LOC | Initial Score | Projected Score | Total Errors | Fixable | Ambiguous | Error Details |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `benchmarks/err_bench_01.py` | PYTHON | 2,461 | 59/100 (D) | 83/100 (B) | **43** | 40 | 3 | L2201:TypeError(fixable/static), L2207:ZeroDivisionError(fixable/static), L2213:IndexError(fixable/static), L2219:IndexError(fixable/static), L2225:KeyError(fixable/static), L2230:ValueError(fixable/static), L2235:ValueError(fixable/static), L2241:LogicalError(fixable/static), L2248:LogicalError(fixable/static), L2253:NameError(fixable/static), L2259:AttributeError(fixable/static), L2265:NameError(fixable/static), L2269:TypeError(fixable/static), L2281:TypeError(fixable/static), L2287:ZeroDivisionError(fixable/static), L2293:IndexError(fixable/static), L2299:IndexError(fixable/static), L2305:KeyError(fixable/static), L2310:ValueError(fixable/static), L2315:ValueError(fixable/static), L2321:LogicalError(fixable/static), L2328:LogicalError(fixable/static), L2333:NameError(fixable/static), L2339:AttributeError(fixable/static), L2345:NameError(fixable/static), L2349:TypeError(fixable/static), L2361:TypeError(fixable/static), L2367:ZeroDivisionError(fixable/static), L2373:IndexError(fixable/static), L2379:IndexError(fixable/static), L2385:KeyError(fixable/static), L2390:ValueError(fixable/static), L2395:ValueError(fixable/static), L2401:LogicalError(fixable/static), L2408:LogicalError(fixable/static), L2413:NameError(fixable/static), L2419:AttributeError(fixable/static), L2425:NameError(fixable/static), L2429:TypeError(fixable/static), L2441:NameError(ambiguous/static), L2446:ValueError(ambiguous/static), L2453:LogicalError(ambiguous/static), L2435:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_02.py` | PYTHON | 2,541 | 60/100 (C) | 83/100 (B) | **43** | 40 | 3 | L2274:IndexError(fixable/static), L2280:KeyError(fixable/static), L2285:ValueError(fixable/static), L2290:ValueError(fixable/static), L2296:LogicalError(fixable/static), L2303:LogicalError(fixable/static), L2308:NameError(fixable/static), L2314:AttributeError(fixable/static), L2320:NameError(fixable/static), L2324:TypeError(fixable/static), L2336:TypeError(fixable/static), L2342:ZeroDivisionError(fixable/static), L2348:IndexError(fixable/static), L2354:IndexError(fixable/static), L2360:KeyError(fixable/static), L2365:ValueError(fixable/static), L2370:ValueError(fixable/static), L2376:LogicalError(fixable/static), L2383:LogicalError(fixable/static), L2388:NameError(fixable/static), L2394:AttributeError(fixable/static), L2400:NameError(fixable/static), L2404:TypeError(fixable/static), L2416:TypeError(fixable/static), L2422:ZeroDivisionError(fixable/static), L2428:IndexError(fixable/static), L2434:IndexError(fixable/static), L2440:KeyError(fixable/static), L2445:ValueError(fixable/static), L2450:ValueError(fixable/static), L2456:LogicalError(fixable/static), L2463:LogicalError(fixable/static), L2468:NameError(fixable/static), L2474:AttributeError(fixable/static), L2480:NameError(fixable/static), L2484:TypeError(fixable/static), L2496:TypeError(fixable/static), L2502:ZeroDivisionError(fixable/static), L2508:IndexError(fixable/static), L2520:ValueError(ambiguous/static), L2527:LogicalError(ambiguous/static), L2534:NameError(ambiguous/static), L2515:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_03.py` | PYTHON | 2,618 | 60/100 (C) | 83/100 (B) | **44** | 41 | 3 | L2346:ValueError(fixable/static), L2352:LogicalError(fixable/static), L2359:LogicalError(fixable/static), L2364:NameError(fixable/static), L2370:AttributeError(fixable/static), L2376:NameError(fixable/static), L2380:TypeError(fixable/static), L2392:TypeError(fixable/static), L2398:ZeroDivisionError(fixable/static), L2404:IndexError(fixable/static), L2410:IndexError(fixable/static), L2416:KeyError(fixable/static), L2421:ValueError(fixable/static), L2426:ValueError(fixable/static), L2432:LogicalError(fixable/static), L2439:LogicalError(fixable/static), L2444:NameError(fixable/static), L2450:AttributeError(fixable/static), L2456:NameError(fixable/static), L2460:TypeError(fixable/static), L2472:TypeError(fixable/static), L2478:ZeroDivisionError(fixable/static), L2484:IndexError(fixable/static), L2490:IndexError(fixable/static), L2496:KeyError(fixable/static), L2501:ValueError(fixable/static), L2506:ValueError(fixable/static), L2512:LogicalError(fixable/static), L2519:LogicalError(fixable/static), L2524:NameError(fixable/static), L2530:AttributeError(fixable/static), L2536:NameError(fixable/static), L2540:TypeError(fixable/static), L2552:TypeError(fixable/static), L2558:ZeroDivisionError(fixable/static), L2564:IndexError(fixable/static), L2570:IndexError(fixable/static), L2576:KeyError(fixable/static), L2581:ValueError(fixable/static), L2586:ValueError(fixable/static), L2599:LogicalError(ambiguous/static), L2606:NameError(ambiguous/static), L2611:ValueError(ambiguous/static), L2592:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_04.py` | PYTHON | 2,625 | 59/100 (D) | 83/100 (B) | **45** | 42 | 3 | L2346:NameError(fixable/static), L2352:AttributeError(fixable/static), L2358:NameError(fixable/static), L2362:TypeError(fixable/static), L2374:TypeError(fixable/static), L2380:ZeroDivisionError(fixable/static), L2386:IndexError(fixable/static), L2392:IndexError(fixable/static), L2398:KeyError(fixable/static), L2403:ValueError(fixable/static), L2408:ValueError(fixable/static), L2414:LogicalError(fixable/static), L2421:LogicalError(fixable/static), L2426:NameError(fixable/static), L2432:AttributeError(fixable/static), L2438:NameError(fixable/static), L2442:TypeError(fixable/static), L2454:TypeError(fixable/static), L2460:ZeroDivisionError(fixable/static), L2466:IndexError(fixable/static), L2472:IndexError(fixable/static), L2478:KeyError(fixable/static), L2483:ValueError(fixable/static), L2488:ValueError(fixable/static), L2494:LogicalError(fixable/static), L2501:LogicalError(fixable/static), L2506:NameError(fixable/static), L2512:AttributeError(fixable/static), L2518:NameError(fixable/static), L2522:TypeError(fixable/static), L2534:TypeError(fixable/static), L2540:ZeroDivisionError(fixable/static), L2546:IndexError(fixable/static), L2552:IndexError(fixable/static), L2558:KeyError(fixable/static), L2563:ValueError(fixable/static), L2568:ValueError(fixable/static), L2574:LogicalError(fixable/static), L2581:LogicalError(fixable/static), L2586:NameError(fixable/static), L2592:AttributeError(fixable/static), L2605:NameError(ambiguous/static), L2610:ValueError(ambiguous/static), L2617:LogicalError(ambiguous/static), L2599:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_05.py` | PYTHON | 2,703 | 59/100 (D) | 83/100 (B) | **45** | 42 | 3 | L2419:TypeError(fixable/static), L2431:TypeError(fixable/static), L2437:ZeroDivisionError(fixable/static), L2443:IndexError(fixable/static), L2449:IndexError(fixable/static), L2455:KeyError(fixable/static), L2460:ValueError(fixable/static), L2465:ValueError(fixable/static), L2471:LogicalError(fixable/static), L2478:LogicalError(fixable/static), L2483:NameError(fixable/static), L2489:AttributeError(fixable/static), L2495:NameError(fixable/static), L2499:TypeError(fixable/static), L2511:TypeError(fixable/static), L2517:ZeroDivisionError(fixable/static), L2523:IndexError(fixable/static), L2529:IndexError(fixable/static), L2535:KeyError(fixable/static), L2540:ValueError(fixable/static), L2545:ValueError(fixable/static), L2551:LogicalError(fixable/static), L2558:LogicalError(fixable/static), L2563:NameError(fixable/static), L2569:AttributeError(fixable/static), L2575:NameError(fixable/static), L2579:TypeError(fixable/static), L2591:TypeError(fixable/static), L2597:ZeroDivisionError(fixable/static), L2603:IndexError(fixable/static), L2609:IndexError(fixable/static), L2615:KeyError(fixable/static), L2620:ValueError(fixable/static), L2625:ValueError(fixable/static), L2631:LogicalError(fixable/static), L2638:LogicalError(fixable/static), L2643:NameError(fixable/static), L2649:AttributeError(fixable/static), L2655:NameError(fixable/static), L2659:TypeError(fixable/static), L2671:TypeError(fixable/static), L2682:ValueError(ambiguous/static), L2689:LogicalError(ambiguous/static), L2696:NameError(ambiguous/static), L2677:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_06.py` | PYTHON | 2,233 | 80/100 (B) | 99/100 (A) | **5** | 5 | 0 | L2201:ZeroDivisionError(fixable/static), L2207:IndexError(fixable/static), L2213:IndexError(fixable/static), L2219:KeyError(fixable/static), L2226:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_07.py` | PYTHON | 2,239 | 80/100 (B) | 84/100 (B) | **6** | 5 | 1 | L2201:KeyError(fixable/static), L2206:ValueError(fixable/static), L2211:ValueError(fixable/static), L2217:LogicalError(fixable/static), L2231:LogicalError(ambiguous/static), L2224:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_08.py` | PYTHON | 2,233 | 81/100 (B) | 99/100 (A) | **5** | 5 | 0 | L2201:LogicalError(fixable/static), L2208:LogicalError(fixable/static), L2213:NameError(fixable/static), L2219:AttributeError(fixable/static), L2226:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_09.py` | PYTHON | 2,303 | 81/100 (B) | 99/100 (A) | **4** | 4 | 0 | L2274:AttributeError(fixable/static), L2280:NameError(fixable/static), L2284:TypeError(fixable/static), L2296:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_10.py` | PYTHON | 2,311 | 80/100 (B) | 84/100 (B) | **5** | 4 | 1 | L2280:TypeError(fixable/static), L2286:ZeroDivisionError(fixable/static), L2292:IndexError(fixable/static), L2304:ValueError(ambiguous/static), L2299:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_11.py` | PYTHON | 2,377 | 80/100 (B) | 99/100 (A) | **5** | 5 | 0 | L2347:IndexError(fixable/static), L2353:IndexError(fixable/static), L2359:KeyError(fixable/static), L2364:ValueError(fixable/static), L2370:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_12.py` | PYTHON | 2,386 | 80/100 (B) | 84/100 (B) | **6** | 5 | 1 | L2346:ValueError(fixable/static), L2351:ValueError(fixable/static), L2357:LogicalError(fixable/static), L2364:LogicalError(fixable/static), L2378:LogicalError(ambiguous/static), L2371:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_13.py` | PYTHON | 2,376 | 81/100 (B) | 99/100 (A) | **5** | 5 | 0 | L2347:LogicalError(fixable/static), L2352:NameError(fixable/static), L2358:AttributeError(fixable/static), L2364:NameError(fixable/static), L2369:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_14.py` | PYTHON | 2,450 | 81/100 (B) | 99/100 (A) | **4** | 4 | 0 | L2420:NameError(fixable/static), L2424:TypeError(fixable/static), L2436:TypeError(fixable/static), L2443:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_15.py` | PYTHON | 2,019 | 79/100 (B) | 84/100 (B) | **6** | 5 | 1 | L1982:TypeError(fixable/static), L1988:ZeroDivisionError(fixable/static), L1994:IndexError(fixable/static), L2000:IndexError(fixable/static), L2012:NameError(ambiguous/static), L2006:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_16.py` | PYTHON | 2,085 | 80/100 (B) | 99/100 (A) | **5** | 5 | 0 | L2055:IndexError(fixable/static), L2061:KeyError(fixable/static), L2066:ValueError(fixable/static), L2071:ValueError(fixable/static), L2078:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_17.py` | PYTHON | 2,090 | 80/100 (B) | 84/100 (B) | **6** | 5 | 1 | L2054:ValueError(fixable/static), L2060:LogicalError(fixable/static), L2067:LogicalError(fixable/static), L2072:NameError(fixable/static), L2083:ValueError(ambiguous/static), L2078:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_18.py` | PYTHON | 2,157 | 80/100 (B) | 99/100 (A) | **5** | 5 | 0 | L2127:NameError(fixable/static), L2133:AttributeError(fixable/static), L2139:NameError(fixable/static), L2143:TypeError(fixable/static), L2150:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_19.py` | PYTHON | 2,158 | 81/100 (B) | 99/100 (A) | **4** | 4 | 0 | L2127:TypeError(fixable/static), L2139:TypeError(fixable/static), L2145:ZeroDivisionError(fixable/static), L2151:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_20.py` | PYTHON | 2,166 | 79/100 (B) | 84/100 (B) | **6** | 5 | 1 | L2128:ZeroDivisionError(fixable/static), L2134:IndexError(fixable/static), L2140:IndexError(fixable/static), L2146:KeyError(fixable/static), L2159:NameError(ambiguous/static), L2153:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_20_fixed.py` | PYTHON | 2,166 | 84/100 (B) | — | **1** | 0 | 1 | L2159:NameError(ambiguous/static) |
| `benchmarks/err_bench_21.py` | PYTHON | 2,231 | 81/100 (B) | 99/100 (A) | **5** | 5 | 0 | L2201:KeyError(fixable/static), L2206:ValueError(fixable/static), L2211:ValueError(fixable/static), L2217:LogicalError(fixable/static), L2224:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_22.py` | PYTHON | 2,238 | 80/100 (B) | 84/100 (B) | **6** | 5 | 1 | L2201:LogicalError(fixable/static), L2208:LogicalError(fixable/static), L2213:NameError(fixable/static), L2219:AttributeError(fixable/static), L2231:ValueError(ambiguous/static), L2226:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_23.py` | PYTHON | 2,303 | 81/100 (B) | 99/100 (A) | **4** | 4 | 0 | L2274:AttributeError(fixable/static), L2280:NameError(fixable/static), L2284:TypeError(fixable/static), L2296:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_24.py` | PYTHON | 2,306 | 81/100 (B) | 99/100 (A) | **4** | 4 | 0 | L2280:TypeError(fixable/static), L2286:ZeroDivisionError(fixable/static), L2292:IndexError(fixable/static), L2299:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_25.py` | PYTHON | 2,312 | 80/100 (B) | 84/100 (B) | **6** | 5 | 1 | L2274:IndexError(fixable/static), L2280:IndexError(fixable/static), L2286:KeyError(fixable/static), L2291:ValueError(fixable/static), L2304:LogicalError(ambiguous/static), L2297:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_26.py` | PYTHON | 2,378 | 81/100 (B) | 99/100 (A) | **5** | 5 | 0 | L2346:ValueError(fixable/static), L2351:ValueError(fixable/static), L2357:LogicalError(fixable/static), L2364:LogicalError(fixable/static), L2371:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_27.py` | PYTHON | 2,382 | 80/100 (B) | 84/100 (B) | **6** | 5 | 1 | L2347:LogicalError(fixable/static), L2352:NameError(fixable/static), L2358:AttributeError(fixable/static), L2364:NameError(fixable/static), L2375:NameError(ambiguous/static), L2369:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_28.py` | PYTHON | 2,450 | 81/100 (B) | 99/100 (A) | **4** | 4 | 0 | L2420:NameError(fixable/static), L2424:TypeError(fixable/static), L2436:TypeError(fixable/static), L2443:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_29.py` | PYTHON | 2,013 | 80/100 (B) | 99/100 (A) | **5** | 5 | 0 | L1982:TypeError(fixable/static), L1988:ZeroDivisionError(fixable/static), L1994:IndexError(fixable/static), L2000:IndexError(fixable/static), L2006:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_30.py` | PYTHON | 2,093 | 79/100 (B) | 84/100 (B) | **6** | 5 | 1 | L2055:IndexError(fixable/static), L2061:KeyError(fixable/static), L2066:ValueError(fixable/static), L2071:ValueError(fixable/static), L2085:LogicalError(ambiguous/static), L2078:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_31.py` | PYTHON | 2,085 | 81/100 (B) | 99/100 (A) | **5** | 5 | 0 | L2054:ValueError(fixable/static), L2060:LogicalError(fixable/static), L2067:LogicalError(fixable/static), L2072:NameError(fixable/static), L2078:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_32.py` | PYTHON | 2,090 | 79/100 (B) | 84/100 (B) | **6** | 5 | 1 | L2054:NameError(fixable/static), L2060:AttributeError(fixable/static), L2066:NameError(fixable/static), L2070:TypeError(fixable/static), L2083:NameError(ambiguous/static), L2077:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_33.py` | PYTHON | 2,158 | 81/100 (B) | 99/100 (A) | **4** | 4 | 0 | L2127:TypeError(fixable/static), L2139:TypeError(fixable/static), L2145:ZeroDivisionError(fixable/static), L2151:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_34.py` | PYTHON | 2,160 | 80/100 (B) | 99/100 (A) | **5** | 5 | 0 | L2128:ZeroDivisionError(fixable/static), L2134:IndexError(fixable/static), L2140:IndexError(fixable/static), L2146:KeyError(fixable/static), L2153:ZeroDivisionError(fixable/runtime) |
| `benchmarks/err_bench_35.py` | PYTHON | 2,236 | 80/100 (B) | 84/100 (B) | **6** | 5 | 1 | L2201:KeyError(fixable/static), L2206:ValueError(fixable/static), L2211:ValueError(fixable/static), L2217:LogicalError(fixable/static), L2229:ValueError(ambiguous/static), L2224:AttributeError(fixable/runtime) |
| `benchmarks/err_bench_cpp_36.cpp` | CPP | 2,202 | 80/100 (B) | 98/100 (A) | **5** | 5 | 0 | L2187:MissingSemicolon(fixable/compiler), L2189:AssignmentInCondition(fixable/compiler), L2190:UndeclaredIdentifier(fixable/compiler), L2192:MissingStdPrefix(fixable/compiler), L2192:MissingStdPrefix(fixable/compiler) |
| `benchmarks/err_bench_cpp_37.cpp` | CPP | 2,233 | 80/100 (B) | 83/100 (B) | **6** | 4 | 2 | L2220:CompileError(ambiguous/compiler), L2221:CompileError(ambiguous/compiler), L2221:MissingSemicolon(fixable/compiler), L2223:MissingStdPrefix(fixable/compiler), L2223:UndeclaredIdentifier(fixable/compiler), L2223:MissingStdPrefix(fixable/compiler) |
| `benchmarks/err_bench_cpp_38.cpp` | CPP | 2,236 | 80/100 (B) | 84/100 (B) | **6** | 5 | 1 | L2221:MissingSemicolon(fixable/compiler), L2222:AssignmentInCondition(fixable/compiler), L2223:UndeclaredIdentifier(fixable/compiler), L2225:CompileError(ambiguous/compiler), L2226:MissingStdPrefix(fixable/compiler), L2226:MissingStdPrefix(fixable/compiler) |
| `benchmarks/err_bench_cpp_39.cpp` | CPP | 2,266 | 80/100 (B) | 84/100 (B) | **5** | 4 | 1 | L2253:MissingSemicolon(fixable/compiler), L2254:CompileError(ambiguous/compiler), L2255:UndeclaredIdentifier(fixable/compiler), L2256:MissingStdPrefix(fixable/compiler), L2256:MissingStdPrefix(fixable/compiler) |
| `benchmarks/err_bench_cpp_40.cpp` | CPP | 2,036 | 80/100 (B) | 98/100 (A) | **5** | 5 | 0 | L2022:MissingSemicolon(fixable/compiler), L2024:AssignmentInCondition(fixable/compiler), L2025:MissingStdPrefix(fixable/compiler), L2025:UndeclaredIdentifier(fixable/compiler), L2025:MissingStdPrefix(fixable/compiler) |

---

## 6. Suite 2 — Dedicated Security Guardrail Test Files (25 Files: 7 Standard + 18 Large >= 2,000 LOC)

| File | Suite Type | Lang | LOC | Stage 1 Security Gate | Findings | Triggered Metrics |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `benchmarks/sec_bench_01.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,061 | **BLOCKED (Grade F · 0/100)** | **3** | SEC_01(CRITICAL:L2055), SEC_01(CRITICAL:L2056), SEC_39(LOW:L2056) |
| `benchmarks/sec_bench_02.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,061 | **BLOCKED (Grade F · 0/100)** | **2** | SEC_02(CRITICAL:L2054), SEC_02(CRITICAL:L2055) |
| `benchmarks/sec_bench_03.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,062 | **BLOCKED (Grade F · 0/100)** | **2** | SEC_03(CRITICAL:L2055), SEC_03(CRITICAL:L2056) |
| `benchmarks/sec_bench_04.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,135 | **BLOCKED (Grade F · 0/100)** | **2** | SEC_04(CRITICAL:L2127), SEC_04(CRITICAL:L2128) |
| `benchmarks/sec_bench_05.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,135 | **BLOCKED (Grade F · 0/100)** | **2** | SEC_05(HIGH:L2127), SEC_06(HIGH:L2130) |
| `benchmarks/sec_bench_06.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,207 | **BLOCKED (Grade F · 0/100)** | **2** | SEC_07(HIGH:L2200), SEC_08(HIGH:L2201) |
| `benchmarks/sec_bench_07.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,207 | **BLOCKED (Grade F · 0/100)** | **3** | SEC_09(CRITICAL:L2202), SEC_09(CRITICAL:L2202), SEC_09(CRITICAL:L2202) |
| `benchmarks/sec_bench_08.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,281 | **BLOCKED (Grade F · 0/100)** | **3** | SEC_12(HIGH:L2273), SEC_11(HIGH:L2274), SEC_42(HIGH:L2275) |
| `benchmarks/sec_bench_09.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,281 | **BLOCKED (Grade F · 0/100)** | **2** | SEC_13(MEDIUM:L2274), SEC_14(HIGH:L2275) |
| `benchmarks/sec_bench_10.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,283 | **BLOCKED (Grade F · 0/100)** | **4** | SEC_16(HIGH:L2276), SEC_16(HIGH:L2277), SEC_17(MEDIUM:L2277), SEC_15(HIGH:L2274) |
| `benchmarks/sec_bench_11.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,357 | **BLOCKED (Grade F · 0/100)** | **4** | SEC_17(MEDIUM:L2347), SEC_19(MEDIUM:L2348), SEC_20(MEDIUM:L2351), SEC_18(HIGH:L2349) |
| `benchmarks/sec_bench_12.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,358 | **BLOCKED (Grade F · 0/100)** | **7** | SEC_22(MEDIUM:L2346), SEC_21(LOW:L2348), SEC_25(MEDIUM:L2349), SEC_22(MEDIUM:L2350), SEC_24(HIGH:L2352), SEC_24(HIGH:L2352), SEC_23(MEDIUM:L2351) |
| `benchmarks/sec_bench_13.py` | 2,000+ LOC Security Benchmark | PYTHON | 1,990 | **BLOCKED (Grade F · 0/100)** | **4** | SEC_27(HIGH:L1983), SEC_26(HIGH:L1984), SEC_28(MEDIUM:L1984), SEC_39(LOW:L1984) |
| `benchmarks/sec_bench_14.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,067 | **Passed with Notes (75/100)** | **9** | SEC_29(MEDIUM:L2054), SEC_31(MEDIUM:L2054), SEC_21(LOW:L2055), SEC_30(LOW:L2056), SEC_29(MEDIUM:L2058), SEC_32(MEDIUM:L2059), SEC_34(MEDIUM:L2060), SEC_33(MEDIUM:L2061), SEC_31(MEDIUM:L2062) |
| `benchmarks/sec_bench_15.py` | 2,000+ LOC Security Benchmark | PYTHON | 2,075 | **BLOCKED (Grade F · 0/100)** | **6** | SEC_37(MEDIUM:L2065), SEC_36(MEDIUM:L2069), SEC_45(LOW:L2061), SEC_38(HIGH:L2057), SEC_35(LOW:L2058), SEC_40(MEDIUM:L2060) |
| `benchmarks/sec_bench_cpp_16.cpp` | 2,000+ LOC Security Benchmark | CPP | 2,166 | **BLOCKED (Grade F · 0/100)** | **3** | SEC_41(CRITICAL:L2155), SEC_41(CRITICAL:L2156), SEC_01(CRITICAL:L2157) |
| `benchmarks/sec_bench_cpp_17.cpp` | 2,000+ LOC Security Benchmark | CPP | 2,166 | **BLOCKED (Grade F · 0/100)** | **3** | SEC_45(LOW:L2154), SEC_43(HIGH:L2156), SEC_42(HIGH:L2157) |
| `benchmarks/sec_bench_cpp_18.cpp` | 2,000+ LOC Security Benchmark | CPP | 2,202 | **BLOCKED (Grade F · 0/100)** | **5** | SEC_22(MEDIUM:L2187), SEC_17(MEDIUM:L2189), SEC_44(HIGH:L2190), SEC_12(HIGH:L2191), SEC_16(HIGH:L2192) |
| `test_cpp_security.cpp` | Standard Security Trap | CPP | 564 | **BLOCKED (Grade F · 0/100)** | **1** | SEC_01(CRITICAL:L557) |
| `test_sec_alias.py` | Standard Security Trap | PYTHON | 11 | **BLOCKED (Grade F · 0/100)** | **5** | SEC_01(CRITICAL:L3), SEC_01(CRITICAL:L6), SEC_01(CRITICAL:L7), SEC_39(LOW:L7), SEC_02(CRITICAL:L8) |
| `test_sec_del.py` | Standard Security Trap | PYTHON | 9 | **BLOCKED (Grade F · 0/100)** | **3** | SEC_16(HIGH:L6), SEC_16(HIGH:L7), SEC_17(MEDIUM:L6) |
| `test_sec_escape.py` | Standard Security Trap | PYTHON | 11 | **BLOCKED (Grade F · 0/100)** | **5** | SEC_12(HIGH:L3), SEC_14(HIGH:L6), SEC_09(CRITICAL:L8), SEC_09(CRITICAL:L8), SEC_09(CRITICAL:L8) |
| `test_sec_notes.py` | Standard Security Trap | PYTHON | 16 | **Passed with Notes (46/100)** | **4** | SEC_29(MEDIUM:L4), SEC_21(LOW:L6), SEC_17(MEDIUM:L9), SEC_20(MEDIUM:L10) |
| `test_sec_order.py` | Standard Security Trap | PYTHON | 10 | **BLOCKED (Grade F · 0/100)** | **1** | SEC_01(CRITICAL:L7) |
| `test_security.py` | Standard Security Trap | PYTHON | 39 | **BLOCKED (Grade F · 0/100)** | **6** | SEC_21(LOW:L28), SEC_21(LOW:L29), SEC_01(CRITICAL:L13), SEC_02(CRITICAL:L18), SEC_17(MEDIUM:L24), SEC_17(MEDIUM:L13) |

---

## 7. Subprocess Hardening & Sandboxing Architecture (`sandbox.py`)

To eliminate the vulnerability of host compromise during untrusted code execution, TOACD incorporates a multi-tier sandbox engine:

1. **macOS Kernel Seatbelt Isolation (`SeatbeltSandboxEngine`)**:
   - Utilizes Apple's native `sandbox-exec` with a compiled `.sb` profile (`sandbox_profile.sb`).
   - Enforces kernel-level Mandatory Access Control (MAC).
   - **Network**: Completely disabled (`deny network*`).
   - **Filesystem**: Read-only host filesystem (`deny file-write*`), with write access strictly isolated to per-execution ephemeral scratch directories.
   - **Credential Protection**: Explicit deny rules prevent reads from `~/.ssh`, `~/.aws`, `~/.gnupg`, dotfiles, and system keychains.
   - **Process Controls**: Disallows unauthorized process spawning (`/bin/sh`, `/bin/bash`, `rm`, `curl`) by whitelisting only designated runtime binaries.

2. **Containerized Execution (`DockerSandboxEngine`)**:
   - Provides ephemeral container isolation (`--rm -i --network none --read-only --user 1000:1000 --cap-drop ALL --memory 256m --cpus 1.0`).
   - Supports optional gVisor (`--runtime runsc`) for hardware-independent syscall interception.

3. **In-Process Defense-in-Depth (`AuditHookSandboxEngine`)**:
   - CPython 3.8+ audit hooks (`sys.addaudithook`) intercept subprocess calls, socket creation, ctypes tampering, and sensitive path access at the interpreter level.
   - POSIX `resource.setrlimit` bounds CPU time (`RLIMIT_CPU`), virtual memory (`RLIMIT_AS`), file size write limits (`RLIMIT_FSIZE`), and descriptor limits (`RLIMIT_NOFILE`).

4. **Verification**:
   - Verified via `test_sandbox.py` (12/12 security test cases passing) confirming file write blocking, network blocking, credential access blocking, subprocess blocking, execution timeouts, and safe C++/Python execution.

