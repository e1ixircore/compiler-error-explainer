import sys, json; sys.path.insert(0, ".")
from app import app
c = app.test_client()
code = "a = 1\nprint(zzz)\nd = {}\nprint(d['k'])\n"
r = c.post("/api/analyze", json={"code": code}).get_json()
for i in r["issues"]: print(i["id"], "orig line", i["line"], i["type"], "|", i["source"], "|", i["how_to_fix"])
print("expect NameError@2, KeyError@4 ->", r["by_line"])
r = c.post("/api/analyze", json={"filename":"test10.py"}).get_json()
print(r["issues"][1]["reason"]); print(r["issues"][1]["how_to_fix"], "| hides:", [i["hides_crash"] for i in r["issues"]])
print(c.post("/api/analyze", json={"filename":"test2.py"}).get_json()["issues"][0]["mistake"])
# old UI contract still intact
r = c.post("/api/analyze", json={"filename":"test1.py"}).get_json()
print("legacy keys:", all(k in r for k in ("raw_text","fixed_code","metrics","diagnostics")))
# benchmark still works (it calls repair_loop directly)
import fix_benchmark, app as api
rows = fix_benchmark.run_benchmark(api, 1, write_csv=False); print("benchmark rows:", len(rows), "ok:", sum(x["detected"]==x["truth"] for x in rows))