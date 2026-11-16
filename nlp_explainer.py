"""
nlp_explainer.py - rule-based explainer + auto-fixer (NO LLM, deterministic, testable).

Contract (what app.py relies on) - UNCHANGED:
    explain(ir: dict) -> str              # contains "Mistake", "Reason", "Fix"
    generate_fixed_code(ir, code) -> str  # patched source, or original if unsafe

WHAT CHANGED (same 8 error types, many more variants of each):
  SyntaxError    : missing colon | '=' used instead of '==' in if/while | 'else if' | Python-2 print
                   | unclosed / stray / mismatched brackets (multi-line aware) | unterminated string
                   | missing indented block | unexpected indent | bad un-indent | && || ! ++ --
  NameError      : forgotten import | true/false/null | typo of a variable, function OR builtin
                   | pure case slip (Total/total) | undefined name -> declared with a sensible
                   starting value, placed OUTSIDE the loop it is used in
  TypeError      : text + number (any operand shape) | '5' > 3 / '10' - 2 (text used as number)
                   | for i in 5 | list[n / 2] and range(n / 2) (decimal used as a position)
  ZeroDivision   : any / // % on the line (not just \\w+ operands) | x /= y
  KeyError       : d['a'] | d['a']['b'] chains | counts[w] += 1 (the word-count idiom)
  IndexError     : lst[10] | lst[i] | lst[i + 1] | negative positions
  ModuleNotFound : typo of a standard library (maths -> math) | import a as b | from a import b, c
                   | only the missing name in 'import os, missing'
  ValueError     : int('3.5') | int('abc') | float('x') | int(input(...))

DESIGN RULES (kept from the original):
  * every patch edits ONLY the failing line (or inserts a declaration / import line)
  * edits are made on the AST's exact character spans, not with blind regexes, so strings and
    comments are never touched and the right operand is picked
  * SAFETY GATE: a patch must still parse (a SyntaxError patch may stay broken as long as the
    error did not move backwards)
"""
import ast
import builtins
import difflib
import re
import sys

from static_analyzer import bound_names

OPEN, CLOSE = "([{", ")]}"
PAIR = dict(zip(OPEN, CLOSE))
BLOCK_RE = r"\s*(if|elif|else|for|while|def|class|try|except|finally|with)\b"

# Standard-library modules whose forgotten `import` we repair automatically.
IMPORTABLE = {"math", "random", "sys", "json", "time", "datetime", "re", "os",
              "string", "statistics", "collections", "itertools", "functools"}
# Words from other languages that students type for Python's special values.
LITERAL_ALIASES = {"true": "True", "false": "False", "null": "None", "nil": "None", "none": "None"}
# Builtins we are willing to suggest, but ONLY when the unknown name is being CALLED: suggesting
# `list` for an undefined variable `lst` would silently change the program's meaning.
CALLABLE_BUILTINS = ["print", "len", "range", "input", "int", "str", "float", "sum", "max", "min",
                     "sorted", "abs", "round", "open", "enumerate", "zip", "list", "dict", "set",
                     "tuple", "bool", "type", "reversed", "isinstance"]
STDLIB = set(getattr(sys, "stdlib_module_names", ())) or {
    "math", "random", "sys", "json", "time", "datetime", "re", "os", "string", "statistics",
    "collections", "itertools", "functools", "csv", "tkinter", "queue", "configparser", "threading"}
PURE_FUNCS = {"len", "abs", "int", "float", "str", "sum", "min", "max", "round"}
SYM = {ast.Lt: "<", ast.Gt: ">", ast.LtE: "<=", ast.GtE: ">=", ast.Add: "+", ast.Sub: "-",
       ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "//", ast.Mod: "%", ast.Pow: "**"}


# ======================================================================
# LOW-LEVEL HELPERS (text + AST spans)
# ======================================================================
def _indent(line):
    return line[: len(line) - len(line.lstrip())]


def _mask(code):
    """Return (masked, unterminated_strings, first_comment_index).
    `masked` has the same length as `code`, but every character inside a string literal or a comment
    is replaced by \\x00 (newlines are kept). Regexes and bracket counters run on the MASKED text, so
    a '#' or a '(' inside "..." can never fool them. This is the lexer's job, done in 30 lines."""
    out, bad, q, qs, first_c, i, n = [], [], None, -1, -1, 0, len(code)
    hide = lambda ch: ch if ch == "\n" else "\x00"
    while i < n:
        c = code[i]
        if q is None:
            if c == "#":                                   # comment: runs to end of line
                if first_c < 0:
                    first_c = i
                j = code.find("\n", i)
                j = n if j < 0 else j
                out.append("\x00" * (j - i)); i = j; continue
            if c in "'\"":
                q = c * 3 if code.startswith(c * 3, i) else c
                qs = i; out.append("\x00" * len(q)); i += len(q); continue
            out.append(c); i += 1; continue
        if c == "\\" and i + 1 < n:                        # escape inside a string
            out.append("\x00" + hide(code[i + 1])); i += 2; continue
        if code.startswith(q, i):                          # closing quote
            out.append("\x00" * len(q)); i += len(q); q = None; continue
        if c == "\n" and len(q) == 1:                      # one-line string hit end of line: never closed
            bad.append((qs, q)); q = None; out.append("\n"); i += 1; continue
        out.append(hide(c)); i += 1
    if q is not None:
        bad.append((qs, q))
    return "".join(out), bad, first_c


def _split_comment(line):
    """('code part', '# comment part'). Unlike line.find('#'), ignores a '#' inside a string."""
    c = _mask(line)[2]
    return (line[:c], line[c:]) if c >= 0 else (line, "")


def _sub(code, pattern, repl, count=0):
    """Regex-substitute on the MASKED code, but copy the edit into the ORIGINAL text.
    repl(m, g): g(k) returns the original text of group k."""
    masked, out, last, n = _mask(code)[0], [], 0, 0
    for m in re.finditer(pattern, masked):
        out.append(code[last:m.start()])
        out.append(repl(m, lambda k, m=m: code[m.start(k):m.end(k)]))
        last = m.end(); n += 1
        if count and n >= count:
            break
    out.append(code[last:])
    return "".join(out)


def _brackets(code):
    """-> (still_open, anomaly). still_open = [(char, line_idx, col)] never closed;
    anomaly = (kind, line_idx, col, wanted_closer) for the first stray / mismatched closer."""
    stack = []
    for li, ml in enumerate(_mask(code)[0].split("\n")):
        for ci, ch in enumerate(ml):
            if ch in OPEN:
                stack.append((ch, li, ci))
            elif ch in CLOSE:
                if not stack:
                    return stack, ("unmatched", li, ci, None)
                o = stack.pop()
                if PAIR[o[0]] != ch:
                    return stack, ("mismatch", li, ci, PAIR[o[0]])
    return stack, None


def _parse(lines):
    try:
        return ast.parse("\n".join(lines))
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return None


def _on_line(tree, ln):
    """AST nodes that start AND end on source line `ln` (single-line nodes are safe to rewrite)."""
    return [n for n in ast.walk(tree)
            if getattr(n, "lineno", None) == ln and getattr(n, "end_lineno", None) == ln]


def _off(line, col):
    """AST columns are UTF-8 BYTE offsets; convert to Python string indexes."""
    return len(line.encode("utf-8")[:col].decode("utf-8", "ignore"))


def _span(line, n):
    return _off(line, n.col_offset), _off(line, n.end_col_offset)


def _seg(line, n):
    s, e = _span(line, n)
    return line[s:e]


def _apply(line, edits):
    """Apply (start, end, text) edits; when edits are nested keep the OUTERMOST one."""
    keep, last_end = [], -1
    for s, e, t in sorted(set(edits), key=lambda x: (x[0], -x[1])):
        if s >= last_end:
            keep.append((s, e, t)); last_end = e
    for s, e, t in reversed(keep):
        line = line[:s] + t + line[e:]
    return line


def _wrap(seg, node):
    """Parenthesise a sub-expression unless it is already an atom (keeps operator precedence right)."""
    atoms = (ast.Name, ast.Constant, ast.Attribute, ast.Subscript, ast.Call, ast.List, ast.Dict, ast.JoinedStr)
    return seg if isinstance(node, atoms) else f"({seg})"


def _idx(sub):
    """Subscript index, across Python versions (3.8 wraps it in ast.Index)."""
    s = sub.slice
    return s.value if type(s).__name__ == "Index" else s


def _pure(n):
    """True if evaluating `n` twice is harmless (no calls with side effects, no input())."""
    if isinstance(n, (ast.Constant, ast.Name)):
        return True
    if isinstance(n, ast.Attribute):
        return _pure(n.value)
    if isinstance(n, ast.Subscript):
        return _pure(n.value) and _pure(_idx(n))
    if isinstance(n, ast.UnaryOp):
        return _pure(n.operand)
    if isinstance(n, ast.BinOp):
        return _pure(n.left) and _pure(n.right)
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in PURE_FUNCS and not n.keywords:
        return all(_pure(a) for a in n.args)
    return False


def _is_int_const(n):
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
        n = n.operand
    return isinstance(n, ast.Constant) and isinstance(n.value, int) and not isinstance(n.value, bool)


def _strish(n):
    """Is this expression obviously TEXT? (literal, f-string, str(...), or text built with +)."""
    if isinstance(n, ast.Constant):
        return isinstance(n.value, str)
    if isinstance(n, ast.JoinedStr):
        return True
    if isinstance(n, ast.Call):
        f = n.func
        return (isinstance(f, ast.Name) and f.id == "str") or \
               (isinstance(f, ast.Attribute) and f.attr in ("format", "join", "strip", "upper", "lower", "title")
                and _strish(f.value))
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return _strish(n.left) or _strish(n.right)
    return False


def _visible(tree, ln):
    """Symbol table at line `ln`: module names + the params/locals of every function containing it."""
    names = set(bound_names(tree.body))
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.lineno <= ln <= (n.end_lineno or n.lineno):
            a = n.args
            names |= {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
            names |= {x.arg for x in (a.vararg, a.kwarg) if x}
            names |= bound_names(n.body)
    return names


def _closest(bad, tree, ln, code):
    """Best 'did you mean' for an undefined name, or None."""
    cands = _visible(tree, ln) - {bad}
    called = re.search(rf"(?<![\w.]){re.escape(bad)}\s*\(", _mask(code)[0])
    if called:
        cands |= set(CALLABLE_BUILTINS)
    cands |= {m for m in IMPORTABLE if len(m) > 2}          # maht -> math (the import is added next pass)
    low = {c.lower(): c for c in cands}
    if bad.lower() in low and low[bad.lower()] != bad:       # only the capitalisation was wrong
        return low[bad.lower()]
    m = difflib.get_close_matches(bad, cands, n=1, cutoff=0.75)
    return m[0] if m else None


def _stdlib_near(name):
    cands = [m for m in STDLIB if not m.startswith("_")]
    low = {m.lower(): m for m in cands}
    if name.lower() in low and low[name.lower()] != name:    # Random -> random, Tkinter -> tkinter
        return low[name.lower()]
    if len(name) < 4 or name in STDLIB:
        return None
    m = difflib.get_close_matches(name, cands, n=1, cutoff=0.8)
    return m[0] if m else None


def _import_slot(lines, tree):
    """Where a new `import x` goes: after the docstring, __future__ imports and header comments."""
    slot = 0
    if tree and tree.body:
        b0 = tree.body[0]
        if isinstance(b0, ast.Expr) and isinstance(getattr(b0, "value", None), ast.Constant) \
                and isinstance(b0.value.value, str):
            slot = b0.end_lineno
        for n in tree.body:
            if isinstance(n, ast.ImportFrom) and n.module == "__future__":
                slot = max(slot, n.end_lineno)
    if slot == 0:
        while slot < len(lines) and (not lines[slot].strip() or lines[slot].lstrip().startswith("#")):
            slot += 1
    return slot


def _decl_slot(tree, ln, lines):
    """Where to declare an undefined variable. If the failing line is inside a loop, declare it
    BEFORE the outermost loop (inside the loop it would be reset to its start value every pass)."""
    parent = {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}
    stmts = [n for n in ast.walk(tree) if isinstance(n, ast.stmt) and n.lineno == ln]
    if not stmts:
        return ln - 1, _indent(lines[ln - 1])
    target = cur = stmts[-1]
    while cur is not None and not isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
        if isinstance(cur, (ast.For, ast.AsyncFor, ast.While)):
            target = cur
        cur = parent.get(cur)
    return target.lineno - 1, _indent(lines[target.lineno - 1])


def _infer_init(bad, code):
    """Pick a starting value from HOW the name is used on the failing line (never invent data)."""
    n = re.escape(bad)
    m = _mask(code)[0]
    if re.search(rf"(?<![\w.]){n}\s*\+=\s*\x00", m):
        return "''"
    if re.search(rf"(?<![\w.]){n}\s*(\+=|-=|\*=)", m):
        return "0"
    if re.search(rf"(?<![\w.]){n}\.(append|extend|insert|pop|sort|reverse)\(", m) \
            or re.search(rf"\bin\s+{n}\b", m) or re.search(rf"len\(\s*{n}\s*\)", m):
        return "[]"
    if re.search(rf"(?<![\w.]){n}\.(get|items|keys|values|update|setdefault)\(", m) or \
            re.search(rf"(?<![\w.]){n}\[\s*\x00", m):
        return "{}"
    if re.search(rf"(?<![\w.]){n}\.add\(", m):
        return "set()"
    return "None"


# ======================================================================
# SYNTAX-ERROR RULES.  Each rule returns True if it changed something. Order matters:
# the most specific / most damaging problems (strings, brackets, indentation) come first.
# ======================================================================
def _prev_code(lines, i):
    return next((j for j in range(min(i, len(lines)) - 1, -1, -1)
                 if lines[j].strip() and not lines[j].lstrip().startswith("#")), None)


def _syn_string(msg, lines, i):
    """'hello   ->  'hello'   (the closing quote goes BEFORE trailing ) ] } or : so print('hi) -> print('hi'))"""
    if i >= len(lines) or not re.search(r"unterminated|EOL while|EOF while scanning", msg):
        return False
    line = lines[i]
    bad = _mask(line)[1]
    if not bad or len(bad[0][1]) == 3:
        return False
    qs, q = bad[0]
    head, tail = line[:qs + 1], line[qs + 1:].rstrip()
    opens = len(_brackets(line[:qs])[0])
    block = bool(re.match(BLOCK_RE, line))
    m = re.search(r"([)\]}]*)(:?)$" if block else r"([)\]}]*)()$", tail)
    k = min(len(m.group(1)), opens)
    cut = m.start() + len(m.group(1)) - k
    lines[i] = head + tail[:cut] + q + tail[cut:]
    return True


def _syn_brackets(msg, lines, i):
    """Stray ')' -> removed. Wrong closer ']' for '(' -> corrected. Never-closed '(' '[' '{' -> closed
    at the END OF THE STATEMENT (not blindly at the end of the opener's line)."""
    still, anomaly = _brackets("\n".join(lines))
    if anomaly:
        kind, li, ci, want = anomaly
        ln = lines[li]
        lines[li] = ln[:ci] + (want if kind == "mismatch" else "") + ln[ci + 1:]
        return True
    if not still:
        return False
    li0 = still[0][1]
    base, end = len(_indent(lines[li0])), li0
    while end + 1 < len(lines):                       # does the statement continue on the next line?
        nxt, prev_code = lines[end + 1], _split_comment(lines[end])[0].rstrip()
        if nxt.strip() and (len(_indent(nxt)) > base or prev_code.endswith(tuple(",([{+-*/=%&|"))):
            end += 1
        else:
            break
    code, comment = _split_comment(lines[end])
    closers = "".join(PAIR[c] for c, _, _ in reversed(still))
    lines[end] = code.rstrip() + closers + ((" " + comment) if comment else "")
    return True


def _syn_indent(msg, lines, i):
    m = msg.lower()
    if "expected an indented block" in m:             # `def f():` with no body -> give it a `pass`
        prev = _prev_code(lines, i)
        if prev is None:
            return False
        lines.insert(i, _indent(lines[prev]) + "    pass")
        return True
    if i >= len(lines):
        return False
    if "unexpected indent" in m:                      # line indented for no reason -> align with previous
        prev = _prev_code(lines, i)
        if prev is None:
            return False
        lines[i] = _indent(lines[prev]) + lines[i].lstrip()
        return True
    if "unindent does not match" in m:                # snap to the nearest existing indentation level
        cur = len(_indent(lines[i]))
        levels = {len(_indent(l)) for l in lines[:i] if l.strip()}
        # nearest existing level wins (ties go to the deeper one: a slightly-off line belongs to the block)
        lines[i] = " " * min(levels or {0}, key=lambda x: (abs(x - cur), -x)) + lines[i].lstrip()
        return True
    return False


def _syn_cond_assign(msg, lines, i):
    """if x = 5:  ->  if x == 5:   (only a lone '=' at bracket depth 0, so f(a=1) is left alone)"""
    code, comment = _split_comment(lines[i])
    if not re.match(r"\s*(if|elif|while)\b", code):
        return False
    masked = _mask(code)[0]
    for m in re.finditer(r"(?<![=!<>:+\-*/%&|^@])=(?!=)", masked):
        depth = sum(c in OPEN for c in masked[:m.start()]) - sum(c in CLOSE for c in masked[:m.start()])
        if depth == 0:
            lines[i] = code[:m.start()] + "==" + code[m.end():] + comment
            return True
    return False


def _syn_foreign_ops(msg, lines, i):
    """&& || !x i++ i--  (C/Java habits)  ->  and / or / not / += 1 / -= 1"""
    code, comment = _split_comment(lines[i])
    new = _sub(code, r"\s*&&\s*", lambda m, g: " and ")
    new = _sub(new, r"\s*\|\|\s*", lambda m, g: " or ")
    new = _sub(new, r"!(?!=)\s*", lambda m, g: "not ")
    new = _sub(new, r"^(\s*)([A-Za-z_]\w*)\s*(\+\+|--)\s*;?\s*$",
               lambda m, g: f"{g(1)}{g(2)} {'+=' if g(3) == '++' else '-='} 1")
    if new == code:
        return False
    lines[i] = new + comment
    return True


def _syn_else_if(msg, lines, i):
    code, comment = _split_comment(lines[i])
    new = re.sub(r"^(\s*)else\s+if\b", r"\1elif", code)
    if new == code:
        return False
    lines[i] = new + comment
    return True


def _syn_print2(msg, lines, i):
    """print "hi", x   ->   print("hi", x)   (Python 2 habit)"""
    code, comment = _split_comment(lines[i])
    m = re.match(r"^(\s*)print\s+([^(\s=].*)$", code.rstrip())
    if not m or ">>" in m.group(2):
        return False
    lines[i] = f"{m.group(1)}print({m.group(2).strip().rstrip(',')})" + (" " + comment if comment else "")
    return True


def _syn_colon(msg, lines, i):
    """if x > 3   ->   if x > 3:"""
    code, comment = _split_comment(lines[i])
    if re.match(BLOCK_RE, code) and not code.rstrip().endswith(":"):
        lines[i] = code.rstrip() + ":" + (" " + comment if comment else "")
        return True
    return False


SYNTAX_RULES = (_syn_string, _syn_brackets, _syn_indent, _syn_cond_assign,
                _syn_foreign_ops, _syn_else_if, _syn_print2, _syn_colon)


# ======================================================================
class NLPExplainer:

    # ------------------------------------------------------------------
    # 1. EXPLANATION (IR dict -> plain English for a BEGINNER)
    #    No compiler jargon ("operand", "scope", "AST"): use everyday comparisons instead.
    # ------------------------------------------------------------------
    MEANINGS = {
        "NameError": "Python found a name (a variable or function) that it does not recognise.",
        "TypeError": "An operation was used on a kind of data that does not support it.",
        "ZeroDivisionError": "A number was divided by zero, which has no answer.",
        "SyntaxError": "The code breaks Python's writing rules, so Python cannot read it.",
        "IndentationError": "The spaces at the start of a line do not match the structure of the code.",
        "KeyError": "A dictionary was asked for a key that is not in it.",
        "IndexError": "A list was asked for a position that does not exist.",
        "ValueError": "A value has the right type but its content is not acceptable.",
        "ModuleNotFoundError": "Python could not find the library you tried to import.",
        "TimeoutError": "The program ran too long and was stopped.",
        "NestingError": "The code is stacked too deeply for the tool to analyse safely.",
    }

    def meaning(self, etype):
        return self.MEANINGS.get(etype, "Python stopped because of an unexpected problem.")

    def explain(self, ir):
        etype = ir.get("error_type") or "UnknownError"
        msg = ir.get("error_message") or ""
        line = ir.get("line_number")
        name = self._quoted(msg)
        where = f" on line {line}" if line else ""
        sug = ir.get("suggestion")

        # ---- TypeError: five specific situations, one generic fallback ----
        if "concatenate" in msg or re.search(r"for \+: '(int|float)' and 'str'", msg):
            type_rule = (
                f"You are joining text and a number with +{where}.",
                "In Python, text (like 'Total: ') and numbers (like 5) are different kinds of data, "
                "and + cannot glue them together.",
                "Turn the number into text with str(), e.g. 'Total: ' + str(5).")
        elif "not supported between instances" in msg or "unsupported operand" in msg:
            type_rule = (
                f"Text is being used like a number{where}.",
                "Text such as '5' looks like a number, but Python treats it as words, so it cannot be "
                "compared or used in maths. (Values typed in with input() are always text.)",
                "Convert it first with int(...) or float(...), e.g. int(age) > 18.")
        elif "is not iterable" in msg:
            type_rule = (
                f"A loop is trying to walk through a single number{where}.",
                "A for loop needs something with many items (a list, some text, or range(...)). "
                "A lone number has no items to walk through.",
                "Use range(n) to repeat n times, e.g. for i in range(5):")
        elif "indices must be integers" in msg or "cannot be interpreted as an integer" in msg:
            type_rule = (
                f"A decimal number was used where a whole number is needed{where}.",
                "Positions in a list and the counts in range(...) must be whole numbers, but / always "
                "gives a decimal (6 / 2 is 3.0, not 3).",
                "Use // for whole-number division, e.g. items[n // 2].")
        else:
            type_rule = (
                f"Two different kinds of data are being combined{where}.",
                f"Python does not allow this operation on these data types. Python said: {msg}",
                "Convert one of the values so both are the same kind, e.g. str(5) or int('5').")

        # ---- NameError: forgotten import / other-language literal / typo / never created ----
        if name in IMPORTABLE:
            name_rule = (f"The library '{name}' is used{where} but was never imported.",
                         "Python's standard libraries must be brought in with an import line "
                         "before their names can be used.",
                         f"Add 'import {name}' at the top of the file.")
        elif name.lower() in LITERAL_ALIASES and name not in LITERAL_ALIASES.values():
            right = LITERAL_ALIASES[name.lower()]
            name_rule = (f"'{name}' is not a Python word{where}.",
                         "Python spells its special values True, False and None with a capital first "
                         "letter. 'true', 'false', 'null' and 'nil' come from other languages.",
                         f"Write {right} instead of {name}.")
        else:
            name_rule = (
                f"The name '{name}'{where} has not been created yet.",
                "Python only knows a variable once you give it a value. Either it was never created, "
                "or it is spelled differently from where you created it."
                + (f" Did you mean '{sug}'?" if sug else ""),
                (f"Change it to '{sug}' if that was your intention, otherwise create " if sug else "Create ")
                + "the variable before this line, e.g. " + (name or "x") + " = 0.")

        near = _stdlib_near(name.split(".")[0]) if name else None
        rules = {
            "NameError": name_rule,
            "TypeError": type_rule,
            "ZeroDivisionError": (
                f"The program divides a number by zero{where}.",
                "Dividing by 0 has no answer in maths, so Python stops with an error.",
                "Make sure the number you divide by is never 0, for example check it with an if first."),
            "SyntaxError": (
                f"Python cannot understand line {line}." if line else "Python cannot understand one of your lines.",
                f"It is written in a way Python's grammar does not allow (Python said: {msg}). "
                "The most common causes are a missing ':' at the end of an if/for/while/def line, "
                "a single '=' where '==' was meant, or a bracket or quote that was opened but never closed.",
                "Check the end of this line and the line above it for a missing ':' or a missing closing bracket."),
            "IndentationError": (
                f"The spacing at the start of line {line} is wrong." if line else "The spacing at the start of a line is wrong.",
                "Python uses the spaces at the start of a line to know which lines belong inside an "
                "if, for, while or def. Here a block is empty, indented too far, or does not line up "
                "with the lines around it.",
                "Indent the body of every if/for/while/def by the same amount (4 spaces) and keep the "
                "lines of one block aligned."),
            "KeyError": (
                f"You asked a dictionary for a key it does not have{where}.",
                f"A dictionary works like a phone book: looking up '{name}' fails if there is no entry with that name.",
                "Check the spelling of the key, or use dict.get(key), which gives None instead of crashing."),
            "IndexError": (
                f"You asked for a list item that does not exist{where}.",
                "List positions start at 0, so a list with 3 items has positions 0, 1 and 2. "
                "This position is past the end of the list.",
                "Use a position smaller than len(your_list), or check the length first."),
            "ValueError": (
                f"The value has the right type but the wrong content{where}.",
                f"For example, int('hello') fails because 'hello' is not a number. Python said: {msg}",
                "Check the value before converting it, or wrap the conversion in try/except."),
            "ModuleNotFoundError": (
                f"Python cannot find a library called '{name}'{where}.",
                "Either the library is not installed on this computer, or its name is misspelled."
                + (f" Did you mean '{near}'?" if near else ""),
                (f"Change the name to '{near}' if that was your intention, otherwise install it" if near
                 else "Check the spelling, or install it") + f" with: pip install {name}"),
            "TimeoutError": (
                "The program ran for more than 5 seconds and was stopped.",
                "This usually means a loop that never ends, such as while True without a way to break out.",
                "Make sure every loop has a condition that eventually becomes false, or a break."),
            "NestingError": (
                "The code is nested too deeply to be analysed safely.",
                "Too many brackets or operations are stacked inside each other.",
                "Split the long expression into several smaller lines."),
        }
        mistake, reason, fix = rules.get(etype, (
            f"A {etype} occurred{where}.",
            msg or "Python gave no further detail.",
            "Read the error message from the bottom up and look at the line it points to."))
        return f"Mistake: {mistake}\nReason: {reason}\nFix: {fix}"

    # ------------------------------------------------------------------
    # 2. AUTO-FIX (IR + source -> patched source)
    # ------------------------------------------------------------------
    def generate_fixed_code(self, ir, code):
        etype = ir.get("error_type")
        line_no = ir.get("line_number")
        lines = code.split("\n")
        syntax = etype in ("SyntaxError", "IndentationError")
        # a missing block at the very end of the file is reported one line PAST the last line
        if not line_no or line_no > len(lines) + (1 if syntax else 0):
            return code
        patcher = getattr(self, f"_fix_{etype}", None)
        if patcher is None:
            return code                      # no rule for this error: change nothing

        patched = list(lines)
        try:
            patcher(ir, patched, line_no - 1)
        except Exception:                    # a buggy rule must never take the server down
            return code
        new_code = "\n".join(patched)
        if new_code == code:
            return code

        # SAFETY GATE (mini patch validator): a patch must still parse.
        try:
            ast.parse(new_code)
        except SyntaxError as e:
            # Python reports ONE syntax error at a time. A patch to a syntax error may leave the file
            # unparsable as long as the first error did not move BACKWARDS (= no regression).
            # app.py's seen_states / repeat counter / pass cap guarantee the loop still terminates.
            if syntax and e.lineno and e.lineno >= line_no:
                return new_code
            return code
        except (RecursionError, ValueError, MemoryError):
            return code
        return new_code

    # ---- helpers ------------------------------------------------------
    @staticmethod
    def _quoted(msg):
        m = re.search(r"'([^']+)'", msg or "")
        return m.group(1) if m else ""

    # ---- SyntaxError / IndentationError ---------------------------------
    def _fix_SyntaxError(self, ir, lines, i):
        msg = ir.get("error_message") or ""
        for rule in SYNTAX_RULES:
            if rule(msg, lines, i):
                return

    _fix_IndentationError = _fix_SyntaxError   # IndentationError IS a SyntaxError subclass

    # ---- NameError -------------------------------------------------------
    def _rename(self, lines, i, bad, new):
        code, comment = _split_comment(lines[i])
        pat = rf"(?<![\w.]){re.escape(bad)}(?!\w)"          # not obj.bad, not bad2
        out = _sub(code, pat, lambda m, g: new)
        if out == code and re.search(r"[fF][\"']", code):    # the name lives inside an f-string {name}
            out = re.sub(rf"(\{{[^{{}}]*?){pat}", lambda m: m.group(1) + new, code, count=1)
        if out == code:
            return False
        lines[i] = out + comment
        return True

    def _fix_NameError(self, ir, lines, i):
        bad = ir.get("error_variable") or self._quoted(ir.get("error_message"))
        if not bad:
            return
        ln, tree = i + 1, _parse(lines)
        code, _ = _split_comment(lines[i])
        # 1. forgotten import of a standard library
        if bad in IMPORTABLE:
            lines.insert(_import_slot(lines, tree), f"import {bad}")
            return
        # 2. true / false / null typed from another language
        if bad.lower() in LITERAL_ALIASES and bad not in LITERAL_ALIASES.values():
            if self._rename(lines, i, bad, LITERAL_ALIASES[bad.lower()]):
                return
        # 3. typo of a name that exists (Levenshtein-style similarity over the symbol table)
        near = ir.get("suggestion") or (_closest(bad, tree, ln, code) if tree else None)
        if near and near != bad and self._rename(lines, i, bad, near):
            return
        # 4. really undefined: declare it, but do NOT invent data
        if tree is None or code.strip().startswith(("elif", "else", "except", "finally")):
            return
        slot, ind = _decl_slot(tree, ln, lines)
        lines.insert(slot, f"{ind}{bad} = {_infer_init(bad, code)}  # TODO: define a real value")

    # ---- TypeError -------------------------------------------------------
    def _fix_TypeError(self, ir, lines, i):
        msg = ir.get("error_message") or ""
        tree = _parse(lines)
        if tree is None:
            return
        line, here, edits = lines[i], _on_line(tree, i + 1), []
        cm = re.search(r"'(<=|>=|<|>)' not supported between instances of '(\w+)' and '(\w+)'", msg)
        am = re.search(r"unsupported operand type\(s\) for (\*\*|//|[-*/%]): '(\w+)' and '(\w+)'", msg)

        if "concatenate" in msg or re.search(r"for \+: '(int|float)' and 'str'", msg) or not msg:
            # text + number: wrap the non-text side of EVERY text-building + on the line in str(...)
            for n in here:
                if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
                    ls, rs = _strish(n.left), _strish(n.right)
                    if ls != rs:
                        s, e = _span(line, n.right if ls else n.left)
                        edits.append((s, e, f"str({line[s:e]})"))
        elif cm or am:
            # '5' > 3  /  '10' - 2 : the message tells us WHICH side is the text
            sym, lt, rt = (cm or am).groups()
            side = "left" if lt == "str" else "right" if rt == "str" else None
            for n in here:
                if side is None:
                    break
                if cm and isinstance(n, ast.Compare) and len(n.ops) == 1 and SYM.get(type(n.ops[0])) == sym:
                    t = n.left if side == "left" else n.comparators[0]
                elif am and isinstance(n, ast.BinOp) and SYM.get(type(n.op)) == sym:
                    t = n.left if side == "left" else n.right
                else:
                    continue
                s, e = _span(line, t)
                if isinstance(t, ast.Constant) and isinstance(t.value, str):
                    if not re.fullmatch(r"\s*-?\d+(\.\d+)?\s*", t.value):
                        continue                      # 'abc' > 5 has no sensible numeric reading
                    edits.append((s, e, t.value.strip()))     # '18' -> 18
                else:
                    edits.append((s, e, f"int({line[s:e]})"))   # int(age)
        elif "'int' object is not iterable" in msg:
            iters = [n.iter for n in ast.walk(tree) if isinstance(n, (ast.For, ast.AsyncFor, ast.comprehension))
                     and getattr(n.iter, "lineno", None) == i + 1 == getattr(n.iter, "end_lineno", None)]
            for it in iters:
                if not (isinstance(it, ast.Call) and isinstance(it.func, ast.Name) and it.func.id == "range"):
                    s, e = _span(line, it)
                    edits.append((s, e, f"range({line[s:e]})"))
        elif "indices must be integers" in msg or "cannot be interpreted as an integer" in msg or "slice indices" in msg:
            zones = []
            for n in here:
                if isinstance(n, ast.Subscript):
                    zones.append(_idx(n))
                elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "range":
                    zones += n.args
            for z in zones:
                for d in ast.walk(z):
                    if isinstance(d, ast.BinOp) and isinstance(d.op, ast.Div) and d.lineno == d.end_lineno == i + 1:
                        le, rs = _span(line, d.left)[1], _span(line, d.right)[0]
                        k = line.find("/", le, rs)
                        if k >= 0:
                            edits.append((k, k + 1, "//"))
        new = _apply(line, edits)
        if new != line:
            lines[i] = new

    # ---- ZeroDivisionError ---------------------------------------------
    def _fix_ZeroDivisionError(self, ir, lines, i):
        tree = _parse(lines)
        if tree is None:
            return
        line, here = lines[i], _on_line(tree, i + 1)
        note = "  # [auto-fix] guarded division, yields 0 if the divisor is 0"
        DIV = (ast.Div, ast.FloorDiv, ast.Mod)
        # x /= y   ->   if y != 0: x /= y      (x stays unchanged instead of becoming a fake 0)
        for n in here:
            if isinstance(n, ast.AugAssign) and isinstance(n.op, DIV) and _pure(n.value):
                s, e = _span(line, n)
                if line[:s].strip() == "":
                    r = line[_span(line, n.value)[0]:_span(line, n.value)[1]]
                    tail = line[e:]
                    lines[i] = f"{line[:s]}if {r} != 0: {line[s:e]}" + (tail if tail.strip() else "  # [auto-fix] skipped when the divisor is 0")
                    return
        edits = []
        for n in here:
            if isinstance(n, ast.BinOp) and isinstance(n.op, DIV) and _pure(n.right):
                if isinstance(n.right, ast.Constant) and isinstance(n.right.value, (int, float)) and n.right.value != 0:
                    continue                          # dividing by a non-zero literal can never be the culprit
                l, r = _wrap(_seg(line, n.left), n.left), _wrap(_seg(line, n.right), n.right)
                s, e = _span(line, n)
                edits.append((s, e, f"({l} {SYM[type(n.op)]} {r} if {r} != 0 else 0)"))
        new = _apply(line, edits)
        if new != line:
            code, comment = _split_comment(new)
            lines[i] = code.rstrip() + note + (" " + comment if comment else "")

    # ---- IndexError ----------------------------------------------------
    def _fix_IndexError(self, ir, lines, i):
        tree = _parse(lines)
        if tree is None:
            return
        line, cands = lines[i], []
        for n in _on_line(tree, i + 1):
            if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Load):
                ix = _idx(n)
                if isinstance(ix, ast.Slice) or (isinstance(ix, ast.Constant) and not isinstance(ix.value, int)):
                    continue                          # slices never raise IndexError; 'key' means dict
                if _pure(n.value) and _pure(ix):
                    cands.append((n, ix))
        # One candidate -> it must be the culprit. Several -> only guard obvious int positions
        # (lst[10]); guarding a dict lookup such as d[key] with len() would change working code.
        pick = cands if len(cands) == 1 else [(n, ix) for n, ix in cands if _is_int_const(ix)]
        edits = []
        for n, ix in pick:
            v, k = _wrap(_seg(line, n.value), n.value), _wrap(_seg(line, ix), ix)
            nonneg = isinstance(ix, ast.Constant) and ix.value >= 0
            cond = f"len({v}) > {k}" if nonneg else f"-len({v}) <= {k} < len({v})"   # also covers negatives
            s, e = _span(line, n)
            edits.append((s, e, f"({v}[{k}] if {cond} else None)"))
        new = _apply(line, edits)
        if new != line:
            lines[i] = new

    # ---- KeyError ------------------------------------------------------
    def _fix_KeyError(self, ir, lines, i):
        tree = _parse(lines)
        if tree is None:
            return
        line, here = lines[i], _on_line(tree, i + 1)
        # counts[w] += 1   ->   counts[w] = counts.get(w, 0) + 1     (the classic word-count crash)
        for n in here:
            if isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Subscript):
                ix, op = _idx(n.target), {ast.Add: "+", ast.Sub: "-", ast.Mult: "*"}.get(type(n.op))
                s, e = _span(line, n)
                if op and not isinstance(ix, ast.Slice) and _pure(n.target.value) and _pure(ix) and not line[:s].strip():
                    v = n.value
                    default = "1" if op == "*" else "''" if isinstance(v, ast.Constant) and isinstance(v.value, str) \
                        else "[]" if isinstance(v, ast.List) else "0"
                    t, k = _seg(line, n.target.value), _seg(line, ix)
                    lines[i] = line[:s] + f"{t}[{k}] = {t}.get({k}, {default}) {op} {_wrap(_seg(line, v), v)}" + line[e:]
                    return
        # Subscripts that are being ASSIGNED TO can't be replaced by .get(): leave them alone.
        stores = set()
        for st in ast.walk(tree):
            if isinstance(st, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Delete, ast.For)) and getattr(st, "lineno", 0) == i + 1:
                tg = st.targets if isinstance(st, (ast.Assign, ast.Delete)) else [st.target]
                stores |= {id(x) for t in tg for x in ast.walk(t)}
        subs = [n for n in here if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Load)
                and id(n) not in stores and not isinstance(_idx(n), ast.Slice)]
        strkey = [n for n in subs if isinstance(_idx(n), ast.Constant) and isinstance(_idx(n).value, str)]
        chosen = strkey or (subs if len(subs) == 1 else [])     # d['k'] is surely a dict; otherwise only if unambiguous
        cset = set(map(id, chosen))

        def conv(n, outer):
            """d['a']['b'] -> d.get('a', {}).get('b'): inner levels default to {} so the chain survives."""
            inner = n.value
            base = conv(inner, False) if id(inner) in cset else _wrap(_seg(line, inner), inner)
            k = _seg(line, _idx(n))
            return f"{base}.get({k})" if outer else f"{base}.get({k}, {{}})"
        edits = [(*_span(line, n), conv(n, True)) for n in chosen]
        new = _apply(line, edits)
        if new != line:
            lines[i] = new

    # ---- ModuleNotFoundError -------------------------------------------
    def _fix_ModuleNotFoundError(self, ir, lines, i):
        ind = _indent(lines[i])
        code, comment = _split_comment(lines[i])
        mod = self._quoted(ir.get("error_message"))
        top = mod.split(".")[0]
        try:
            st = ast.parse(code.strip()).body[0]
        except (SyntaxError, IndexError):
            st = None

        def guarded(stmt_text, bound):
            names = " = ".join(bound) if bound else "pass"
            return [f"{ind}try:", f"{ind}    {stmt_text}", f"{ind}except ImportError:",
                    f"{ind}    {names + ' = None  # module unavailable' if bound else 'pass'}"]

        near = _stdlib_near(top) if top else None
        if isinstance(st, ast.Import):
            out = []
            for a in st.names:
                bound = a.asname or a.name.split(".")[0]
                text = f"import {a.name}" + (f" as {a.asname}" if a.asname else "")
                if a.name.split(".")[0] != top:
                    out.append(f"{ind}{text}")                       # a module that is fine stays as it is
                elif near and "." not in a.name:
                    out.append(f"{ind}import {near} as {bound}")     # import maths -> import math as maths
                else:
                    out += guarded(text, [bound])
            lines[i:i + 1] = out
        elif isinstance(st, ast.ImportFrom):
            names = ", ".join(a.name + (f" as {a.asname}" if a.asname else "") for a in st.names)
            if near and st.level == 0:
                lines[i] = f"{ind}from {near} import {names}" + (("  " + comment) if comment else "")
            else:
                bound = [] if names == "*" else [a.asname or a.name for a in st.names]
                lines[i:i + 1] = guarded(code.strip(), bound)
        else:                                                         # unusual shape: old behaviour
            lines[i:i + 1] = guarded(code.strip(), [top] if top else [])

    # ---- ValueError ----------------------------------------------------
    def _fix_ValueError(self, ir, lines, i):
        msg = ir.get("error_message") or ""
        tree = _parse(lines)
        if tree is None:
            return
        line, edits = lines[i], []
        floaty = re.search(r"'[-+]?\d+\.\d+'", msg)           # int('3.5'): the text is a decimal number
        for n in _on_line(tree, i + 1):
            if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("int", "float")
                    and len(n.args) == 1 and not n.keywords):
                continue
            a, fn = n.args[0], n.func.id
            if isinstance(a, ast.Constant):
                if not isinstance(a.value, str):
                    continue                                  # int(5) / int(3.5) can never raise ValueError
                try:
                    (int if fn == "int" else float)(a.value); continue   # converts fine: not the culprit
                except ValueError:
                    pass
            s, e = _span(line, n)
            arg = line[_span(line, a)[0]:_span(line, a)[1]]
            if fn == "int" and floaty:
                edits.append((s, e, f"int(float({arg}))"))    # int('3.5') -> int(float('3.5')) = 3
                continue
            ok = "{v}.strip().lstrip('+-').isdigit()" if fn == "int" else \
                 "{v}.strip().replace('.', '', 1).lstrip('+-').isdigit()"
            if _pure(a):
                v, first = arg, arg
            else:                                             # int(input(..)): evaluate ONCE with :=
                v, first = "_v", f"_v := {arg}"
            # non-text values pass straight through, so working int(3.7) calls are not changed
            edits.append((s, e, f"({fn}({v}) if not isinstance({first}, str) or {ok.format(v=v)} else 0)"))
        new = _apply(line, edits)
        if new != line:
            lines[i] = new