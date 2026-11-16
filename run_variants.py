# run_variants.py - pushes MANY variants of each error type through the REAL pipeline
# (repair_loop -> verify_fix). Same idea as run_checks.py, but for breadth: it shows how many
# different shapes of each error type the tool can now fix.
#   python run_variants.py            # table of verdicts
#   python run_variants.py -v         # also prints the fixed code of every case
import sys
from app import repair_loop, verify_fix, scan

CASES = {
 "SyntaxError": {
  "missing colon (def)":        "def f(x)\n    return x\nprint(f(1))\n",
  "'=' instead of '=='":        "x = 5\nif x = 5:\n    print('five')\n",
  "'=' AND missing colon":      "x = 5\nif x = 5\n    print('five')\n",
  "else if":                    "x = 1\nif x > 3:\n    print('big')\nelse if x > 0:\n    print('small')\n",
  "python-2 print":             "name = 'Sam'\nprint 'Hello', name\n",
  "unclosed paren":             "print('hi'\n",
  "unclosed nested paren":      "x = [1, 2, 3]\nprint(len(x)\n",
  "unclosed list over lines":   "x = [1,\n     2,\n     3\nprint(x)\n",
  "stray closing paren":        "print('hi'))\n",
  "wrong closing bracket":      "x = [1, 2, 3)\nprint(x)\n",
  "unterminated string":        "msg = 'hello\nprint(msg)\n",
  "unterminated in call":       "print('hello)\n",
  "empty function body":        "def todo():\nprint('x')\n",
  "unexpected indent":          "x = 1\n    y = 2\nprint(x, y)\n",
  "bad un-indent":              "def f():\n    a = 1\n  b = 2\n    return a + b\nprint(f())\n",
  "&& and ||":                  "a, b = 1, 2\nif a > 0 && b > 0 || a < 0:\n    print('ok')\n",
  "i++":                        "i = 0\ni++\nprint(i)\n",
  "'#' inside string + colon":  "for i in range(3)\n    print('#', i)\n",
 },
 "NameError": {
  "typo variable":              "total = 5\nprint(totl)\n",
  "typo in f-string":           "total = 5\nprint(f'Total: {totl}')\n",
  "typo of function":           "def calculate(a):\n    return a\nprint(calcualte(2))\n",
  "typo of builtin call":       "pritn('hi')\n",
  "case slip":                  "Total = 5\nprint(total)\n",
  "forgot import math":         "print(math.sqrt(16))\n",
  "forgot import random":       "x = random.randint(1, 6)\nprint(x >= 1)\n",
  "true / null":                "x = true\ny = null\nprint(x, y)\n",
  "accumulator in loop":        "for i in range(3):\n    count += 1\nprint(count)\n",
  "list in loop":               "for i in range(3):\n    out.append(i)\nprint(out)\n",
  "dict usage":                 "cache.get('a')\n",
  "for over undefined":         "for x in items:\n    print(x)\n",
  "typo inside function":       "def f(price, qty):\n    return pirce * qty\nprint(f(2, 3))\n",
 },
 "TypeError": {
  "'text' + 5":                 "print('Total: ' + 5)\n",
  "'text' + variable":          "n = 5\nprint('Total: ' + n)\n",
  "'text' + len(x)":            "x = [1, 2]\nprint('Items: ' + len(x))\n",
  "number + 'text'":            "n = 5\nprint(n + ' items')\n",
  "chained concat":             "a, b = 1, 2\nprint('a=' + a + ' b=' + b)\n",
  "'text' + (a + b)":           "a, b = 1, 2\nprint('Sum: ' + (a + b))\n",
  "compare '18' > 3":           "age = '20'\nif age > 18:\n    print('adult')\n",
  "compare literal":            "if '10' > 3:\n    print('ok')\n",
  "text - number":              "price = '10'\nprint(price - 2)\n",
  "for i in 5":                 "n = 3\nfor i in n:\n    print(i)\n",
  "list[n / 2]":                "a = [1, 2, 3, 4]\nn = len(a)\nprint(a[n / 2])\n",
  "range(n / 2)":               "n = 6\nfor i in range(n / 2):\n    print(i)\n",
 },
 "ZeroDivisionError": {
  "10 / 0":                     "print(10 / 0)\n",
  "a / b (b=0)":                "a, b = 4, 0\nprint(a / b)\n",
  "second division fails":      "print(10 / 2, 5 / 0)\n",
  "complex divisor":            "a, b = 3, 3\nprint(10 / (a - b))\n",
  "len() divisor":              "xs = []\nprint(sum(xs) / len(xs))\n",
  "modulo":                     "print(7 % 0)\n",
  "x /= y":                     "x, y = 8, 0\nx /= y\nprint(x)\n",
  "floor div in function":      "def avg(t, n):\n    return t // n\nprint(avg(5, 0))\n",
 },
 "KeyError": {
  "d['b']":                     "d = {'a': 1}\nprint(d['b'])\n",
  "assign + read same line":    "d = {'a': 1}\nd['x'] = d['y']\nprint(d)\n",
  "nested d['a']['b']":         "d = {'a': {'b': 1}}\nprint(d['z']['b'])\n",
  "counts[w] += 1":             "counts = {}\nfor w in ['a', 'b', 'a']:\n    counts[w] += 1\nprint(counts)\n",
  "variable key":               "d = {'a': 1}\nk = 'q'\nprint(d[k])\n",
 },
 "IndexError": {
  "lst[10]":                    "lst = [1, 2, 3]\nprint(lst[10])\n",
  "two subscripts, 2nd bad":    "a = [1]\nb = [1, 2]\nprint(a[0] + b[5])\n",
  "variable index":             "lst = [1, 2, 3]\ni = 7\nprint(lst[i])\n",
  "i + 1 (off-by-one)":         "lst = [1, 2, 3]\nfor i in range(3):\n    print(lst[i + 1])\n",
  "negative index":             "lst = []\nprint(lst[-1])\n",
  "matrix[r][c]":               "m = [[1, 2], [3, 4]]\nprint(m[0][5])\n",
 },
 "ModuleNotFoundError": {
  "typo stdlib (maths)":        "import maths\nprint(maths.sqrt(4))\n",
  "wrong case (Random)":        "import Random\nprint(Random.randint(1, 1))\n",
  "unknown module":             "import missing_helper\nprint('after')\n",
  "import x as y":              "import missing_helper as mh\nprint(mh)\n",
  "from x import a, b":         "from missing_pkg import a, b\nprint(a, b)\n",
  "dotted import":              "import missing_pkg.sub\nprint('after')\n",
  "one bad name in list":       "import os, missing_helper\nprint(os.sep, missing_helper)\n",
  "inside a function":          "def f():\n    import missing_helper\n    return missing_helper\nprint(f())\n",
 },
 "ValueError": {
  "int('abc')":                 "age = int('seventeen')\nprint(age)\n",
  "int('3.5')":                 "n = int('3.5')\nprint(n)\n",
  "float('x')":                 "v = float('abc')\nprint(v)\n",
  "int(variable)":              "s = 'twelve'\nprint(int(s) + 1)\n",
 },
}


def main(verbose):
    ok = total = 0
    for etype, group in CASES.items():
        print(f"\n== {etype} ==")
        for label, code in group.items():
            total += 1
            if scan(code)[2]:
                print(f"  {label:30} BLOCKED"); continue
            fixed, hist = repair_loop(code)
            v = verify_fix(code, fixed)["verdict"]
            ok += v == "VERIFIED"
            passes = sum(h.get("result") == "patched" for h in hist)
            print(f"  {label:30} {v:18} patches={passes}")
            if verbose or v != "VERIFIED":
                for l in fixed.rstrip().split("\n"):
                    print("      | " + l)
                if v != "VERIFIED":
                    print("      ! " + verify_fix(code, fixed)["detail"])
    print(f"\nVERIFIED {ok}/{total}")


if __name__ == "__main__":
    main("-v" in sys.argv)