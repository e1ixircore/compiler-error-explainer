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
  ValueError     : int('3.5') | int('abc') | int('seventeen') | float('x') | int(input(...))

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
from word2number import w2n
from cst_patcher import apply_functional_cst_fix

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


from ir_generator import cached_ast_parse


def _parse(lines):
    return cached_ast_parse("\n".join(lines))


def _on_line(tree, ln):
    """AST nodes that start AND end on source line `ln` (single-line nodes are safe to rewrite)."""
    root = tree
    for stmt in getattr(tree, "body", ()):
        start = getattr(stmt, "lineno", 0)
        end = getattr(stmt, "end_lineno", start)
        if start <= ln <= end:
            root = stmt
            break
    return [n for n in ast.walk(root)
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


_TYPE_DEFAULTS = {
    "int": "0",
    "float": "0.0",
    "str": "''",
    "bool": "False",
    "list": "[]",
    "dict": "{}",
    "set": "set()",
    "tuple": "()",
    "None": "None",
    "NoneType": "None",
}

_STR_METHODS = {
    "upper", "lower", "strip", "lstrip", "rstrip", "split", "rsplit", "splitlines",
    "startswith", "endswith", "replace", "title", "capitalize", "casefold",
    "isdigit", "isalpha", "isalnum", "isnumeric", "isspace", "isupper", "islower",
    "swapcase", "zfill", "center", "ljust", "rjust",
}


def _enclosing_func(tree, ln):
    best = None
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.lineno <= ln <= (n.end_lineno or n.lineno):
            if best is None or n.lineno >= best.lineno:
                best = n
    return best


def _ann_base_name(ann):
    if ann is None:
        return None
    if isinstance(ann, ast.Name):
        return ann.id
    if isinstance(ann, ast.Constant):
        if ann.value is None:
            return "None"
        if isinstance(ann.value, str):
            return ann.value.strip()
    if isinstance(ann, ast.Subscript):
        return _ann_base_name(ann.value)
    return None


def _return_default_for_line(tree, ln):
    """If line `ln` is a return statement inside a function with a concrete return annotation,
    return a matching default literal string (e.g. '0' for -> int), else None."""
    fn = _enclosing_func(tree, ln)
    if not fn or not fn.returns:
        return None
    is_ret = any(isinstance(n, ast.Return) and getattr(n, "lineno", None) == ln for n in ast.walk(fn))
    if not is_ret:
        return None
    base = _ann_base_name(fn.returns)
    return _TYPE_DEFAULTS.get(base)


def _infer_init(bad, code, tree=None, ln=None):
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
    if tree is not None and ln is not None:
        ret_def = _return_default_for_line(tree, ln)
        if ret_def is not None:
            return ret_def
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
        "AttributeError": "An object was asked for a property or action (method) that it does not have.",
        "ModuleNotFoundError": "Python could not find the library you tried to import.",
        "LogicalError": "The code is valid Python, but its logic does something different from what you intended.",
        "UnboundLocalError": "A local variable inside a function was read before a value was assigned to it.",
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
        elif "return type mismatch" in msg:
            type_rule = (
                f"The function returns a value whose type does not match its return annotation{where}.",
                f"The function promises one kind of data in its return type hint, but a different kind is returned ({msg}).",
                "Return a value of the declared type, or update the function's return type annotation.")
        elif "incompatible type in assignment" in msg:
            type_rule = (
                f"A variable is assigned a value that does not match its type annotation{where}.",
                f"The variable was annotated with one type, but given a different type of value ({msg}).",
                "Assign a value of the declared type, or change the variable's type annotation to match.")
        elif "has no len()" in msg:
            type_rule = (
                f"len() was called on a value that has no length{where}.",
                f"len() only works on collections or text (such as lists, strings, or dicts), not single numbers or None ({msg}).",
                "Pass a list or string to len(), or convert the number with str(...) if you want its digit count.")
        elif "missing" in msg and "positional argument" in msg or "takes" in msg and "positional argument" in msg:
            type_rule = (
                f"A function was called with the wrong number of arguments{where}.",
                f"The function definition expects a specific number of inputs, but the call did not match ({msg}).",
                "Pass the required argument(s) inside the parentheses when calling the function (edit the line in the manual patch box below).")
        else:
            type_rule = (
                f"Two different kinds of data are being combined{where}.",
                f"Python does not allow this operation on these data types. Python said: {msg}",
                "Convert one of the values so both are the same kind, e.g. str(5) or int('5').")

        # ---- LogicalError: identity 'is' with literal / tuple assert / self-comparison ----
        if "identity operator" in msg:
            logic_rule = (
                f"You used 'is' (or 'is not') to compare a value with a literal{where}.",
                "In Python, 'is' checks whether two objects live at the exact same memory address, not whether their values are equal. For numbers and text, 'is' can produce the wrong answer.",
                "Use '==' (or '!=') to compare values instead of 'is'.")
        elif "non-empty tuple" in msg:
            logic_rule = (
                f"An assert statement was written with outer parentheses like assert(condition, message){where}.",
                "In Python, assert(a, b) tests whether the 2-item tuple (a, b) is non-empty. Because a 2-item tuple is ALWAYS truthy, this assertion never triggers even when the condition is False!",
                "Remove the outer parentheses so it reads: assert condition, message")
        elif "self-comparison" in msg:
            logic_rule = (
                f"The variable '{name}' is being compared to itself{where}.",
                "Comparing a variable to itself (such as x == x or x != x) always evaluates to the same True/False constant no matter what value the variable holds. Usually you meant to compare it against another variable.",
                "Edit the right-hand side of the comparison in the manual patch box below to use the intended variable or threshold.")
        else:
            logic_rule = (
                f"A logical flaw was detected{where}.",
                msg or "The code runs without crashing, but its condition or operation always produces an unintended result.",
                "Review the condition or expression on this line and update it to match your intended logic.")

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
            "AttributeError": (
                f"An attribute or method was used on a value that may not support it{where}.",
                f"Only certain data types have certain methods (for example, .upper() exists on text, not numbers). Python said: {msg}",
                "Check the value's type first with isinstance(...) or hasattr(...), or convert it with str(...) before calling string methods."),
            "ModuleNotFoundError": (
                f"Python cannot find a library called '{name}'{where}.",
                "Either the library is not installed on this computer, or its name is misspelled."
                + (f" Did you mean '{near}'?" if near else ""),
                (f"Change the name to '{near}' if that was your intention, otherwise install it" if near
                 else "Check the spelling, or install it") + f" with: pip install {name}"),
            "LogicalError": logic_rule,
            "UnboundLocalError": (
                f"The local variable '{name}'{where} is used before a value is assigned to it inside this function.",
                "Because this function assigns to '" + (name or "x") + "' later on, Python treats it as a local variable for the whole function, so reading it before that assignment fails.",
                f"Give '{name or 'x'}' an initial value at the start of the function, or fix the variable spelling."),
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
    _CST_AUTO_FIX_TYPES = {
        "NameError", "TypeError", "AttributeError", "KeyError",
        "ModuleNotFoundError", "ValueError", "LogicalError",
    }

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

        # Primary engine: direct Concrete Syntax Tree (LibCST) mutation for parseable code.
        # Preserves comments, multi-line expressions, and mixed whitespace without string slicing.
        new_code = code
        if etype in self._CST_AUTO_FIX_TYPES:
            msg = ir.get("error_message") or ""
            suggestion = ir.get("suggestion")
            fn_ret = None
            tree = _parse(lines)
            if etype == "NameError" and not suggestion and tree is not None and 1 <= line_no <= len(lines):
                bad = ir.get("error_variable") or self._quoted(msg)
                if bad:
                    code_part, _ = _split_comment(lines[line_no - 1])
                    suggestion = _closest(bad, tree, line_no, code_part)
            elif etype == "TypeError" and "incompatible type in assignment" in msg and tree is not None:
                rm = re.search(r"assignment to '([^']+)'", msg)
                if rm:
                    var_name = rm.group(1)
                    fn = _enclosing_func(tree, line_no)
                    if fn is not None and any(
                        isinstance(r, ast.Return) and isinstance(r.value, ast.Name) and r.value.id == var_name
                        for r in ast.walk(fn)
                    ):
                        fn_ret = _ann_base_name(fn.returns)
            cst_fixed, _, _ = apply_functional_cst_fix(
                code,
                error_type=etype,
                error_message=msg,
                line_no=line_no,
                suggestion=suggestion,
                error_variable=ir.get("error_variable"),
                fn_return_type=fn_ret,
                contextual=False,
            )
            if cst_fixed != code:
                new_code = cst_fixed

        # Fallback to rule-based patchers (required for SyntaxError/IndentationError where no CST exists yet)
        if new_code == code:
            patched = list(lines)
            try:
                patcher(ir, patched, line_no - 1)
            except Exception:                    # a buggy rule must never take the server down
                return code
            new_code = "\n".join(patched)

        if new_code == code:
            return code

        # SAFETY GATE (mini patch validator): a patch must still parse.
        if not syntax:
            return new_code if cached_ast_parse(new_code) is not None else code
        try:
            ast.parse(new_code)
        except SyntaxError as e:
            # Python reports ONE syntax error at a time. A patch to a syntax error may leave the file
            # unparsable as long as the first error did not move BACKWARDS (= no regression).
            # app.py's seen_states / repeat counter / pass cap guarantee the loop still terminates.
            if e.lineno and e.lineno >= line_no:
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
        # 4. Truly undefined variable/function with no typo match: explain-only (do not invent stubs).
        return

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
        elif "has no len()" in msg:
            for n in here:
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "len" and len(n.args) == 1:
                    arg = n.args[0]
                    s, e = _span(line, arg)
                    edits.append((s, e, f"str({line[s:e]})"))
        elif "return type mismatch" in msg:
            # Only auto-fix lossless conversions (e.g. -> str, or numeric string "42" -> 42).
            # Non-numeric mismatches like `return "wrong type"` for `-> int` are explain-only.
            rm = re.search(r"expected '([^']+)', got '([^']+)'", msg)
            exp = rm.group(1).split(" | ")[0].strip() if rm else None
            for n in here:
                if isinstance(n, ast.Return) and n.value is not None and exp:
                    val = n.value
                    s, e = _span(line, val)
                    seg = line[s:e]
                    if exp == "str":
                        edits.append((s, e, f"str({seg})"))
                    elif isinstance(val, ast.Constant) and isinstance(val.value, str) \
                            and exp in ("int", "float") and re.fullmatch(r"\s*-?\d+(\.\d+)?\s*", val.value):
                        num = str(int(float(val.value))) if exp == "int" else str(float(val.value))
                        edits.append((s, e, num))
        elif "incompatible type in assignment" in msg:
            rm = re.search(r"assignment to '([^']+)': expected '([^']+)', got '([^']+)'", msg)
            if rm:
                var_name, exp, got = rm.groups()
                exp = exp.split(" | ")[0].strip()
                got = got.split(" | ")[0].strip()
                fn = _enclosing_func(tree, i + 1)
                fn_ret = _ann_base_name(fn.returns) if fn else None
                # If the variable is returned from a function whose return annotation matches `got`,
                # fix the variable's type annotation so the whole function becomes type-consistent.
                returned_here = fn is not None and any(
                    isinstance(r, ast.Return) and isinstance(r.value, ast.Name) and r.value.id == var_name
                    for r in ast.walk(fn)
                )
                for n in here:
                    if isinstance(n, ast.AnnAssign) and n.value is not None:
                        if returned_here and fn_ret == got and got in _TYPE_DEFAULTS:
                            s, e = _span(line, n.annotation)
                            edits.append((s, e, got))
                        else:
                            val = n.value
                            s, e = _span(line, val)
                            seg = line[s:e]
                            if exp == "str":
                                edits.append((s, e, f"str({seg})"))
                            elif isinstance(val, ast.Constant) and isinstance(val.value, str) \
                                    and exp in ("int", "float") and re.fullmatch(r"\s*-?\d+(\.\d+)?\s*", val.value):
                                num = str(int(float(val.value))) if exp == "int" else str(float(val.value))
                                edits.append((s, e, num))
        new = _apply(line, edits)
        if new != line:
            lines[i] = new

    # ---- AttributeError ------------------------------------------------
    def _fix_AttributeError(self, ir, lines, i):
        msg = ir.get("error_message") or ""
        tree = _parse(lines)
        if tree is None:
            return
        m = re.search(r"attribute '([^']+)'", msg)
        attr_name = m.group(1) if m else None
        line, here, edits = lines[i], _on_line(tree, i + 1), []
        for n in here:
            if isinstance(n, ast.Attribute) and (attr_name is None or n.attr == attr_name):
                if n.attr in _STR_METHODS:
                    s, e = _span(line, n.value)
                    edits.append((s, e, f"str({line[s:e]})"))
        new = _apply(line, edits)
        if new != line:
            lines[i] = new

    # ---- ZeroDivisionError (explain-only: no fake `if 0 != 0 else 0` workarounds) ----
    def _fix_ZeroDivisionError(self, ir, lines, i):
        return

    # ---- IndexError (explain-only: no silent out-of-bounds fallback workarounds) -------
    def _fix_IndexError(self, ir, lines, i):
        return

    # ---- KeyError ------------------------------------------------------
    def _fix_KeyError(self, ir, lines, i):
        tree = _parse(lines)
        if tree is None:
            return
        line, here = lines[i], _on_line(tree, i + 1)
        # Only auto-fix the idiomatic counter pattern: counts[w] += 1 -> counts[w] = counts.get(w, 0) + 1.
        # Plain missing-key lookups like record["absent"] are explain-only (do not hide with silent defaults).
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

    # ---- ModuleNotFoundError -------------------------------------------
    def _fix_ModuleNotFoundError(self, ir, lines, i):
        # Only auto-fix clear standard-library typos (e.g. `import maths` -> `import math as maths`).
        # Missing third-party libraries are explain-only (suggest `pip install`, do not stub to None).
        ind = _indent(lines[i])
        code, comment = _split_comment(lines[i])
        mod = self._quoted(ir.get("error_message"))
        top = mod.split(".")[0]
        near = _stdlib_near(top) if top else None
        if not near:
            return
        try:
            st = ast.parse(code.strip()).body[0]
        except (SyntaxError, IndexError):
            return
        if isinstance(st, ast.Import):
            out = []
            for a in st.names:
                bound = a.asname or a.name.split(".")[0]
                text = f"import {a.name}" + (f" as {a.asname}" if a.asname else "")
                if a.name.split(".")[0] == top and "." not in a.name:
                    out.append(f"{ind}import {near} as {bound}")
                else:
                    out.append(f"{ind}{text}")
            lines[i:i + 1] = out
        elif isinstance(st, ast.ImportFrom) and st.level == 0:
            names = ", ".join(a.name + (f" as {a.asname}" if a.asname else "") for a in st.names)
            lines[i] = f"{ind}from {near} import {names}" + (("  " + comment) if comment else "")

    # ---- ValueError ----------------------------------------------------
    def _fix_ValueError(self, ir, lines, i):
        # Only auto-fix unambiguous numeric-text conversions:
        #   - English number words: int('seventeen') -> int(17)
        #   - Decimal strings passed to int(): int('3.5') -> int(float('3.5'))
        # Non-numeric strings like int('not-a-number') are explain-only.
        msg = ir.get("error_message") or ""
        tree = _parse(lines)
        if tree is None:
            return
        line, edits = lines[i], []
        floaty = re.search(r"'[-+]?\d+\.\d+'", msg)
        for n in _on_line(tree, i + 1):
            if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("int", "float")
                    and len(n.args) == 1 and not n.keywords):
                continue
            a, fn = n.args[0], n.func.id
            if isinstance(a, ast.Constant):
                if not isinstance(a.value, str):
                    continue
                try:
                    (int if fn == "int" else float)(a.value)
                    continue
                except ValueError:
                    pass
                if fn == "int":
                    try:
                        number = w2n.word_to_num(a.value)
                    except ValueError:
                        pass
                    else:
                        s, e = _span(line, n)
                        edits.append((s, e, f"int({number})"))
                        continue
            if fn == "int" and floaty:
                s, e = _span(line, n)
                arg = line[_span(line, a)[0]:_span(line, a)[1]]
                edits.append((s, e, f"int(float({arg}))"))
        new = _apply(line, edits)
        if new != line:
            lines[i] = new

    # ---- LogicalError --------------------------------------------------
    def _fix_LogicalError(self, ir, lines, i):
        msg = ir.get("error_message") or ""
        line = lines[i]
        code_part, comment = _split_comment(line)
        if "identity operator" in msg:
            # Replace ' is not ' with ' != ' or ' is ' with ' == '
            if re.search(r"\bis\s+not\b", code_part):
                new_code = re.sub(r"\bis\s+not\b", "!=", code_part, count=1)
            else:
                new_code = re.sub(r"\bis\b", "==", code_part, count=1)
            if new_code != code_part:
                lines[i] = new_code + comment
        elif "non-empty tuple" in msg:
            # assert (a, b) -> assert a, b
            m = re.match(r"^(\s*assert)\s*\((.+)\)\s*$", code_part)
            if m:
                lines[i] = f"{m.group(1)} {m.group(2)}{comment}"
        # Note: 'self-comparison' (x == x) is intentionally left as ambiguous / manual patch.