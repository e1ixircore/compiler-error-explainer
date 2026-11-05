# analytics_data.py - the dashboard's data layer.
# RULE: every number returned here comes from a file or a live scan. Nothing is generated,
# randomised or fitted by a formula. If a source is missing, the field is None/empty and the
# dashboard says "no data" instead of inventing a value.
#
# Sources:
#   fix_benchmark_results.csv  <- fix_benchmark.py (real pipeline runs, median of N repeats)
#   powermetrics_log.txt       <- macOS `powermetrics` capture (package power samples)
#   emissions.csv              <- CodeCarbon's own output file
#   test*.py                   <- scanned live by SecurityAnalyzer
import ast
import csv
import glob
import os
import re
import statistics
from datetime import datetime

from security_analyzer import SecurityAnalyzer

BENCH_CSV = "fix_benchmark_results.csv"
POWER_LOG = "powermetrics_log.txt"
CODECARBON_CSV = "emissions.csv"
DEFAULT_POWER_W = 4.7          # only used if powermetrics_log.txt is missing; flagged in the payload


# ----------------------------------------------------------------------
# powermetrics: Intel energy-model package power (CPUs + GT + SA), one value per sample
# ----------------------------------------------------------------------
def load_power(path=POWER_LOG):
    if not os.path.exists(path):
        return {"available": False, "mean_w": DEFAULT_POWER_W, "watts": [], "elapsed_ms": [], "machine": None}
    text = open(path, encoding="utf-8", errors="ignore").read()
    watts = [float(x) for x in re.findall(r"package power \(CPUs\+GT\+SA\):\s*([\d.]+)W", text)]
    elapsed = [float(x) for x in re.findall(r"\(([\d.]+)ms elapsed\)", text)]
    machine = re.search(r"Machine model:\s*(\S+)", text)
    return {"available": bool(watts),
            "mean_w": round(statistics.mean(watts), 3) if watts else DEFAULT_POWER_W,
            "watts": watts, "elapsed_ms": elapsed[:len(watts)],
            "machine": machine.group(1) if machine else None}


# ----------------------------------------------------------------------
# CodeCarbon: read the rows CodeCarbon itself wrote
# ----------------------------------------------------------------------
def load_codecarbon(path=CODECARBON_CSV):
    if not os.path.exists(path):
        return []
    runs = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                f = lambda k: float(r.get(k) or 0)
                # older CodeCarbon files have no total column: sum the components that exist
                kwh = f("energy_consumed") or (f("cpu_energy") + f("ram_energy") + f("gpu_energy"))
                runs.append({
                    "timestamp": r["timestamp"],
                    "duration_s": round(f("duration"), 3),
                    "emissions_mg": round(f("emissions") * 1e6, 3),
                    "energy_mwh": round(kwh * 1e6, 3),
                    "cpu_power_w": f("cpu_power"),      # shows 0 if the column is absent
                    "tracking_mode": r.get("tracking_mode"),
                })
            except (KeyError, ValueError):
                continue
    return runs


# ----------------------------------------------------------------------
# benchmark rows (written by fix_benchmark.py)
# ----------------------------------------------------------------------
def load_benchmark(path=BENCH_CSV):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            for k in ("lines", "patches"):
                r[k] = int(float(r[k])) if r.get(k) not in (None, "") else None
            for k in ("detect_ms", "repair_ms", "verify_ms", "total_ms"):
                r[k] = float(r[k])
            if r["lines"] is None and os.path.exists(r["file"]):       # older CSV without a size column
                r["lines"] = len(open(r["file"], encoding="utf-8", errors="ignore").read().split("\n"))
            rows.append(r)
    return rows


# ----------------------------------------------------------------------
# security: scan every test file live. Unparseable files are reported as SKIPPED,
# because SecurityAnalyzer cannot walk an AST that does not exist.
# ----------------------------------------------------------------------
def security_summary():
    sa = SecurityAnalyzer()
    out = {"labels": [], "CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": [], "skipped": []}
    for f in sorted(glob.glob("test*.py")):
        code = open(f, encoding="utf-8", errors="ignore").read()
        try:
            ast.parse(code)
        except (SyntaxError, ValueError, RecursionError):
            out["skipped"].append(f)
            continue
        found = sa.scan_code(code)
        out["labels"].append(f)
        for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
            out[sev].append(sum(1 for v in found if v["severity"] == sev))
    return out


# ----------------------------------------------------------------------
# the payload the dashboard renders
# ----------------------------------------------------------------------
def build_payload(rows=None):
    rows = load_benchmark() if rows is None else rows
    power = load_power()
    w = power["mean_w"]
    rows = sorted(rows, key=lambda r: (r["lines"] or 0, r["file"]))
    label = lambda r: f"{r['file']} ({r['lines']} lines)"

    stage = {}
    for st in ("static", "runtime"):
        d = [r["detect_ms"] for r in rows if r["stage"] == st]
        stage[st] = {"median_ms": round(statistics.median(d), 3) if d else None, "n": len(d)}

    verdicts = {}
    for r in rows:
        verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1

    generated = (datetime.fromtimestamp(os.path.getmtime(BENCH_CSV)).strftime("%Y-%m-%d %H:%M")
                 if os.path.exists(BENCH_CSV) else None)
    return {
        "has_benchmark": bool(rows),
        "meta": {"files": len(rows), "generated": generated, "power_w": w,
                 "power_is_default": not power["available"], "machine": power["machine"],
                 "power_samples": len(power["watts"])},
        "latency": {"labels": [label(r) for r in rows],
                    "detect": [r["detect_ms"] for r in rows],
                    "repair": [r["repair_ms"] for r in rows],
                    "verify": [r["verify_ms"] for r in rows]},
        "stage": stage,
        "outcomes": {"verdicts": verdicts,
                     "detected_ok": sum(r["detected"] == r["truth"] for r in rows),
                     "total": len(rows)},
        "patches": {"labels": [r["file"] for r in rows], "values": [r["patches"] for r in rows]},
        # energy = measured mean package power x measured time. An ESTIMATE, and labelled as one.
        "energy": {"labels": [label(r) for r in rows],
                   "mJ": [round(w * r["total_ms"], 1) for r in rows]},
        "power": {"labels": [f"#{i + 1}" for i in range(len(power["watts"]))],
                  "watts": power["watts"], "mean_w": w},
        "codecarbon": load_codecarbon(),
        "security": security_summary(),
        "not_measured": ["Pinpoint agent overhead (needs the Pinpoint tool; no data exists in this project)"],
    }