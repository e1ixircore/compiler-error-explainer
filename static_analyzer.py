# static_analyzer.py
import ast, builtins, difflib, sys, importlib.util

_BUILTIN_TYPE_MAP = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "bytes": bytes,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "NoneType": type(None),
}
_TYPE_ATTRS = {name: set(dir(tp)) for name, tp in _BUILTIN_TYPE_MAP.items()}

# Type-specific methods that commonly fail with AttributeError when called on an unguarded `Any`.
_STRICT_ANY_METHODS = {
    "upper", "lower", "strip", "lstrip", "rstrip", "split", "rsplit", "splitlines",
    "startswith", "endswith", "replace", "title", "capitalize", "casefold",
    "isdigit", "isalpha", "isalnum", "isnumeric", "isspace", "isupper", "islower",
    "swapcase", "zfill", "center", "ljust", "rjust",
    "append", "extend", "insert", "sort", "reverse",
}

_NON_SIZED_TYPES = {"int", "float", "bool", "NoneType"}
_NON_NUMERIC_TYPES = {"str", "bytes", "list", "dict", "set", "tuple", "NoneType"}
_NON_INT_INDEX_TYPES = {"str", "float", "bytes", "list", "dict", "set", "tuple", "NoneType"}


def bound_names(body):
    """Names a scope binds. Hoisted so use-before-def inside functions
    doesn't false-positive (functions may reference globals defined later).
    Trade-off: this misses use-before-assignment. Note it in the report."""
    names, stack = set(), list(body)
    while stack:
        n = stack.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(n.name)
            continue                      # nested scope: don't descend
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            names.add(n.id)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                names.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.ExceptHandler) and n.name:
            names.add(n.name)
        stack.extend(ast.iter_child_nodes(n))
    return names


def _sub_index(sub):
    s = sub.slice
    return s.value if type(s).__name__ == "Index" else s


def _annotation_type(node):
    """Resolve a type annotation AST node into a normalized type spec:
    a base type string ('int', 'str', 'list', 'dict', 'Any', 'NoneType', ...),
    a frozenset of strings for Union/Optional, or None if unrecognized."""
    if node is None:
        return None
    if isinstance(node, ast.Constant):
        if node.value is None:
            return "NoneType"
        if isinstance(node.value, str):
            val = node.value.strip()
            if val in _BUILTIN_TYPE_MAP or val == "Any":
                return val
            if val == "None":
                return "NoneType"
            return None
        return None
    if isinstance(node, ast.Name):
        if node.id == "None":
            return "NoneType"
        if node.id in _BUILTIN_TYPE_MAP or node.id == "Any":
            return node.id
        alias = {"List": "list", "Dict": "dict", "Set": "set", "Tuple": "tuple",
                 "Sequence": "list", "Mapping": "dict", "MutableMapping": "dict",
                 "Iterable": "list"}
        return alias.get(node.id)
    if isinstance(node, ast.Attribute):
        return _annotation_type(ast.Name(id=node.attr, ctx=ast.Load()))
    if isinstance(node, ast.Subscript):
        base_name = None
        if isinstance(node.value, ast.Name):
            base_name = node.value.id
        elif isinstance(node.value, ast.Attribute):
            base_name = node.value.attr
        if base_name == "Optional":
            inner = _annotation_type(_sub_index(node))
            if inner is None:
                return None
            parts = set(inner) if isinstance(inner, frozenset) else {inner}
            parts.add("NoneType")
            return frozenset(parts)
        if base_name == "Union":
            sl = _sub_index(node)
            elts = sl.elts if isinstance(sl, ast.Tuple) else [sl]
            parts = set()
            for e in elts:
                t = _annotation_type(e)
                if t is None:
                    return None
                if isinstance(t, frozenset):
                    parts |= t
                else:
                    parts.add(t)
            return frozenset(parts) if parts else None
        return _annotation_type(node.value)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        lt, rt = _annotation_type(node.left), _annotation_type(node.right)
        if lt is None or rt is None:
            return None
        parts = set()
        for t in (lt, rt):
            parts |= t if isinstance(t, frozenset) else {t}
        return frozenset(parts)
    return None


def _type_display(tspec):
    if isinstance(tspec, frozenset):
        return " | ".join(sorted("None" if t == "NoneType" else t for t in tspec))
    return "None" if tspec == "NoneType" else str(tspec)


def _is_compatible(actual, expected):
    """Return True if `actual` type is compatible with `expected` type annotation."""
    if actual is None or expected is None or actual == "Any" or expected == "Any":
        return True
    if isinstance(expected, frozenset):
        if "Any" in expected:
            return True
        return any(_is_compatible(actual, e) for e in expected)
    if isinstance(actual, frozenset):
        if "Any" in actual:
            return True
        return all(_is_compatible(a, expected) for a in actual)
    if actual == expected:
        return True
    if actual == "bool" and expected in ("int", "float"):
        return True
    if actual == "int" and expected == "float":
        return True
    return False


def _eval_int_const(node):
    """Evaluate a pure constant integer expression (e.g. 0, -1, 2 - 2), or return None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        v = _eval_int_const(node.operand)
        if v is not None:
            return -v if isinstance(node.op, ast.USub) else v
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
        l, r = _eval_int_const(node.left), _eval_int_const(node.right)
        if l is not None and r is not None:
            if isinstance(node.op, ast.Add):
                return l + r
            if isinstance(node.op, ast.Sub):
                return l - r
            return l * r
    return None


class StaticChecker(ast.NodeVisitor):
    def __init__(self, tree):
        # Scope stack = the symbol table. Index 0 = builtins, 1 = module globals.
        self.scopes = [set(dir(builtins)), bound_names(tree.body)]
        self.errors = []
        # Denominators proven non-zero by an ENCLOSING guard (`b != 0`).
        # This is a tiny path-sensitive analysis: facts hold only inside the guarded branch.
        self.guarded = set()
        # Bounds, key, attribute, value guards active in the current branch.
        self.index_guarded = set()
        self.key_guarded = set()
        self.attr_guarded = set()
        self.value_guarded = False
        # Active try/except caught exception names.
        self.except_stack = []
        # Type environments per lexical scope (name -> normalized type spec).
        self.type_envs = [{}]
        # Literal sequence length environments (name -> int length).
        self.seq_len_envs = [{}]
        # Literal dict key environments (name -> set of string keys).
        self.dict_key_envs = [{}]
        # Function return annotations stack.
        self.return_stack = []
        # Set of parameter names in the current function explicitly annotated as dict.
        self.param_dict_stack = [set()]
        # Known module-level function return types and parameter arity.
        self.func_returns = {}
        self.func_arity = {}
        for stmt in tree.body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                rt = _annotation_type(stmt.returns)
                if rt is not None:
                    self.func_returns[stmt.name] = rt
                a = stmt.args
                if not a.vararg and not a.kwarg and not a.kwonlyargs and not a.posonlyargs:
                    total_p = len(a.args)
                    def_p = len(a.defaults)
                    self.func_arity[stmt.name] = (total_p - def_p, total_p, [x.arg for x in a.args])

    def _err(self, etype, msg, node, **extra):
        self.errors.append({"error_type": etype, "error_message": msg,
                            "line_number": node.lineno,
                            "column": node.col_offset, **extra})

    def _catches(self, etype):
        for caught in self.except_stack:
            if not caught or etype in caught or "Exception" in caught or "BaseException" in caught:
                return True
        return False

    def _lookup_type(self, name):
        for env in reversed(self.type_envs):
            if name in env:
                return env[name]
        return None

    def _lookup_seq_len(self, name):
        for env in reversed(self.seq_len_envs):
            if name in env:
                return env[name]
        return None

    def _lookup_dict_keys(self, name):
        for env in reversed(self.dict_key_envs):
            if name in env:
                return env[name]
        return None

    def _infer_type(self, node):
        if node is None:
            return None
        if isinstance(node, ast.Constant):
            v = node.value
            if v is None:
                return "NoneType"
            if isinstance(v, bool):
                return "bool"
            if isinstance(v, int):
                return "int"
            if isinstance(v, float):
                return "float"
            if isinstance(v, str):
                return "str"
            if isinstance(v, bytes):
                return "bytes"
            return None
        if isinstance(node, ast.JoinedStr):
            return "str"
        if isinstance(node, (ast.List, ast.ListComp)):
            return "list"
        if isinstance(node, (ast.Dict, ast.DictComp)):
            return "dict"
        if isinstance(node, (ast.Set, ast.SetComp)):
            return "set"
        if isinstance(node, ast.Tuple):
            return "tuple"
        if isinstance(node, ast.Compare):
            return "bool"
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return "bool"
            return self._infer_type(node.operand)
        if isinstance(node, ast.Name):
            return self._lookup_type(node.id)
        if isinstance(node, ast.BinOp):
            lt, rt = self._infer_type(node.left), self._infer_type(node.right)
            if isinstance(node.op, ast.Div):
                if lt in ("int", "float", "bool") and rt in ("int", "float", "bool"):
                    return "float"
            if isinstance(node.op, ast.Add):
                if lt == "str" and rt == "str":
                    return "str"
                if lt == "list" and rt == "list":
                    return "list"
                if lt in ("int", "float", "bool") and rt in ("int", "float", "bool"):
                    return "float" if "float" in (lt, rt) else "int"
            if isinstance(node.op, (ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod, ast.Pow)):
                if isinstance(node.op, ast.Mult) and {lt, rt} == {"str", "int"}:
                    return "str"
                if lt in ("int", "float", "bool") and rt in ("int", "float", "bool"):
                    return "float" if "float" in (lt, rt) else "int"
            return None
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                fn = node.func.id
                builtin_ret = {
                    "len": "int", "int": "int", "float": "float", "str": "str",
                    "bool": "bool", "list": "list", "sorted": "list", "dict": "dict",
                    "set": "set", "tuple": "tuple", "ord": "int", "chr": "str",
                }
                if fn in builtin_ret:
                    return builtin_ret[fn]
                if fn in ("min", "max") and node.args:
                    ts = {self._infer_type(a) for a in node.args}
                    if len(ts) == 1:
                        return next(iter(ts))
                if fn in self.func_returns:
                    return self.func_returns[fn]
            elif isinstance(node.func, ast.Attribute):
                recv_t = self._infer_type(node.func.value)
                if recv_t == "str" and node.func.attr in (
                    "strip", "lstrip", "rstrip", "lower", "upper", "title",
                    "capitalize", "replace", "join", "format", "casefold",
                ):
                    return "str"
                if recv_t == "str" and node.func.attr in ("split", "rsplit", "splitlines"):
                    return "list"
                if recv_t == "str" and node.func.attr.startswith(("is", "starts", "ends")):
                    return "bool"
            return None
        if isinstance(node, ast.IfExp):
            bt, ot = self._infer_type(node.body), self._infer_type(node.orelse)
            # If the else-branch is a stand-in None fallback (e.g. auto-fix guard), don't widen.
            if ot == "NoneType" and bt is not None:
                return bt
            if bt == ot:
                return bt
            if {bt, ot} <= {"int", "float", "bool"}:
                return "float" if "float" in (bt, ot) else "int"
            return None
        return None

    # --- scopes -------------------------------------------------------
    def _function(self, node):
        for d in node.decorator_list:
            self.visit(d)
        a = node.args
        for d in a.defaults + [k for k in a.kw_defaults if k]:
            self.visit(d)
        all_args = a.posonlyargs + a.args + a.kwonlyargs
        params = {x.arg for x in all_args}
        params |= {x.arg for x in (a.vararg, a.kwarg) if x}
        self.scopes.append(params | bound_names(node.body))

        env = {}
        param_dicts = set()
        for arg in all_args:
            t = _annotation_type(arg.annotation)
            if t is not None:
                env[arg.arg] = t
                if t == "dict":
                    param_dicts.add(arg.arg)
        self.type_envs.append(env)
        self.seq_len_envs.append({})
        self.dict_key_envs.append({})
        self.param_dict_stack.append(param_dicts)
        self.return_stack.append(_annotation_type(node.returns))
        for s in node.body:
            self.visit(s)
        self.return_stack.pop()
        self.param_dict_stack.pop()
        self.dict_key_envs.pop()
        self.seq_len_envs.pop()
        self.type_envs.pop()
        self.scopes.pop()
    visit_FunctionDef = visit_AsyncFunctionDef = _function

    def visit_Lambda(self, node):
        a = node.args
        params = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
        self.scopes.append(params)
        self.type_envs.append({})
        self.seq_len_envs.append({})
        self.dict_key_envs.append({})
        self.param_dict_stack.append(set())
        self.visit(node.body)
        self.param_dict_stack.pop()
        self.dict_key_envs.pop()
        self.seq_len_envs.pop()
        self.type_envs.pop()
        self.scopes.pop()

    def visit_ClassDef(self, node):
        self.scopes.append(bound_names(node.body))
        self.type_envs.append({})
        self.seq_len_envs.append({})
        self.dict_key_envs.append({})
        self.param_dict_stack.append(set())
        for s in node.body:
            self.visit(s)
        self.param_dict_stack.pop()
        self.dict_key_envs.pop()
        self.seq_len_envs.pop()
        self.type_envs.pop()
        self.scopes.pop()

    def visit_Try(self, node):
        caught = set()
        for h in node.handlers:
            if h.type is None:
                caught.add("BaseException")
            elif isinstance(h.type, ast.Name):
                caught.add(h.type.id)
            elif isinstance(h.type, ast.Tuple):
                for elt in h.type.elts:
                    if isinstance(elt, ast.Name):
                        caught.add(elt.id)
        self.except_stack.append(caught)
        for s in node.body:
            self.visit(s)
        self.except_stack.pop()
        for h in node.handlers:
            self.visit(h)
        for s in node.orelse:
            self.visit(s)
        for s in node.finalbody:
            self.visit(s)

    # --- guards -------------------------------------------------------
    @staticmethod
    def _nonzero_guard(test):
        """If `test` is `<expr> != 0`, return a fingerprint of <expr>, else None."""
        if (isinstance(test, ast.Compare) and len(test.ops) == 1
                and isinstance(test.ops[0], ast.NotEq)
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == 0):
            return ast.dump(test.left)
        return None

    @staticmethod
    def _collect_guards(test):
        """Extract bounds, key, attribute, and value guards implied when `test` is truthy."""
        idx_g, key_g, attr_g, val_g = set(), set(), set(), False
        nodes = [test]
        if isinstance(test, ast.BoolOp):
            nodes.extend(test.values)
        for sub in nodes:
            # Bounds guard: `len(v) > k`, `k < len(v)`, `0 <= k < len(v)`, `-len(v) <= k < len(v)`
            if isinstance(sub, ast.Compare):
                exprs = [sub.left] + list(sub.comparators)
                for e in exprs:
                    if (isinstance(e, ast.Call) and isinstance(e.func, ast.Name)
                            and e.func.id == "len" and len(e.args) == 1):
                        idx_g.add(ast.dump(e.args[0]))
                # Key membership guard: `k in d`
                if len(sub.ops) == 1 and isinstance(sub.ops[0], ast.In):
                    key_g.add((ast.dump(sub.comparators[0]), ast.dump(sub.left)))
            # Attribute guard: `isinstance(x, ...)` or `hasattr(x, 'attr')`
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                if sub.func.id == "isinstance" and len(sub.args) >= 2:
                    attr_g.add((ast.dump(sub.args[0]), "*"))
                elif sub.func.id == "hasattr" and len(sub.args) >= 2:
                    if isinstance(sub.args[1], ast.Constant) and isinstance(sub.args[1].value, str):
                        attr_g.add((ast.dump(sub.args[0]), sub.args[1].value))
            # Value conversion guard (e.g. `...isdigit()` in auto-fix IfExp)
            for inner in ast.walk(sub):
                if isinstance(inner, ast.Attribute) and inner.attr in ("isdigit", "isnumeric"):
                    val_g = True
        return idx_g, key_g, attr_g, val_g

    def _visit_guarded(self, test, body, orelse):
        # The guard is true ONLY in `body`; in `orelse` it is not known, so it is removed.
        g = self._nonzero_guard(test)
        added = g is not None and g not in self.guarded
        idx_g, key_g, attr_g, val_g = self._collect_guards(test)
        new_idx = idx_g - self.index_guarded
        new_key = key_g - self.key_guarded
        new_attr = attr_g - self.attr_guarded
        prev_val_g = self.value_guarded

        self.visit(test)
        if added:
            self.guarded.add(g)
        self.index_guarded |= new_idx
        self.key_guarded |= new_key
        self.attr_guarded |= new_attr
        if val_g:
            self.value_guarded = True
        for n in body:
            self.visit(n)
        if added:
            self.guarded.discard(g)
        self.index_guarded -= new_idx
        self.key_guarded -= new_key
        self.attr_guarded -= new_attr
        self.value_guarded = prev_val_g
        for n in orelse:
            self.visit(n)

    def visit_IfExp(self, node):          # a / b if b != 0 else 0
        self._visit_guarded(node.test, [node.body], [node.orelse])

    def visit_If(self, node):             # if b != 0: ... a / b ...
        self._visit_guarded(node.test, node.body, node.orelse)

    # --- assignments & returns ----------------------------------------
    def visit_Assign(self, node):
        self.visit(node.value)
        val_t = self._infer_type(node.value)
        for target in node.targets:
            self.visit(target)
            if isinstance(target, ast.Name):
                if val_t is not None and target.id not in self.type_envs[-1]:
                    self.type_envs[-1][target.id] = val_t
                if isinstance(node.value, (ast.List, ast.Tuple)):
                    self.seq_len_envs[-1][target.id] = len(node.value.elts)
                elif isinstance(node.value, ast.Dict):
                    keys = {k.value for k in node.value.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
                    self.dict_key_envs[-1][target.id] = keys

    def visit_AnnAssign(self, node):
        # Intentionally do not visit node.annotation as a Load (avoids forward-ref NameError).
        expected = _annotation_type(node.annotation)
        if node.value is not None:
            self.visit(node.value)
            actual = self._infer_type(node.value)
            if isinstance(node.target, ast.Name):
                if isinstance(node.value, (ast.List, ast.Tuple)):
                    self.seq_len_envs[-1][node.target.id] = len(node.value.elts)
                elif isinstance(node.value, ast.Dict):
                    keys = {k.value for k in node.value.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
                    self.dict_key_envs[-1][node.target.id] = keys
            if expected is not None and actual is not None and not _is_compatible(actual, expected):
                tname = node.target.id if isinstance(node.target, ast.Name) else "variable"
                self._err(
                    "TypeError",
                    f"incompatible type in assignment to '{tname}': expected '{_type_display(expected)}', got '{_type_display(actual)}'",
                    node,
                )
                # Record the actual value's type to avoid cascading a duplicate return-type error
                # on the same variable right below the mismatched assignment.
                if isinstance(node.target, ast.Name):
                    self.type_envs[-1][node.target.id] = actual
                return
        if isinstance(node.target, ast.Name) and expected is not None:
            self.type_envs[-1][node.target.id] = expected

    def visit_Return(self, node):
        if node.value is not None:
            self.visit(node.value)
        if not self.return_stack:
            return
        expected = self.return_stack[-1]
        if expected is None or expected == "Any":
            return
        actual = "NoneType" if node.value is None else self._infer_type(node.value)
        if actual is not None and not _is_compatible(actual, expected):
            self._err(
                "TypeError",
                f"return type mismatch: expected '{_type_display(expected)}', got '{_type_display(actual)}'",
                node,
            )

    # --- checks -------------------------------------------------------
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            visible = set().union(*self.scopes)
            if node.id not in visible:
                # Levenshtein-style "did you mean" from the symbol table itself.
                # Exclude builtins from candidates so we don't suggest `print`.
                user_names = set().union(*self.scopes[1:])
                close = difflib.get_close_matches(node.id, user_names, n=1, cutoff=0.7)
                self._err("NameError", f"name '{node.id}' is not defined", node,
                          suggestion=close[0] if close else None)

    def visit_BinOp(self, node):
        l, r = node.left, node.right
        # Catch obvious type mismatches (constants or inferred types) without running code.
        if isinstance(node.op, ast.Add):
            tl, tr = self._infer_type(l), self._infer_type(r)
            if tl and tr and tl != tr and "str" in (tl, tr) and {tl, tr} <= {"str", "int", "float", "bool"}:
                other = tr if tl == "str" else tl
                self._err("TypeError",
                          f'can only concatenate str (not "{other}") to str',
                          node)
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) \
                and not self._catches("ZeroDivisionError") \
                and ast.dump(r) not in self.guarded:
            r_val = _eval_int_const(r)
            is_zero = (r_val == 0) or (isinstance(r, ast.Constant) and isinstance(r.value, (int, float))
                                       and not isinstance(r.value, bool) and r.value == 0)
            if is_zero:
                self._err("ZeroDivisionError", "division by zero", node)
        self.generic_visit(node)

    def visit_Subscript(self, node):
        if isinstance(node.ctx, ast.Load):
            idx = _sub_index(node)
            val_dump = ast.dump(node.value)
            k = _eval_int_const(idx)
            # 1. Guaranteed out-of-bounds index: seq[len(seq)] or seq[len(seq) + k] (k >= 0),
            #    or literal sequence indexed past its length.
            if not self._catches("IndexError") and val_dump not in self.index_guarded:
                oob = False
                if (isinstance(idx, ast.Call) and isinstance(idx.func, ast.Name)
                        and idx.func.id == "len" and len(idx.args) == 1
                        and ast.dump(idx.args[0]) == val_dump):
                    oob = True
                elif (isinstance(idx, ast.BinOp) and isinstance(idx.op, ast.Add)
                        and isinstance(idx.left, ast.Call) and isinstance(idx.left.func, ast.Name)
                        and idx.left.func.id == "len" and len(idx.left.args) == 1
                        and ast.dump(idx.left.args[0]) == val_dump):
                    k_off = _eval_int_const(idx.right)
                    if k_off is not None and k_off >= 0:
                        oob = True
                elif isinstance(node.value, (ast.List, ast.Tuple)):
                    n = len(node.value.elts)
                    if k is not None and (k >= n or k < -n):
                        oob = True
                elif isinstance(node.value, ast.Name):
                    n = self._lookup_seq_len(node.value.id)
                    if n is not None and k is not None and (k >= n or k < -n):
                        oob = True
                if oob:
                    self._err("IndexError", "list index out of range", node)

            # 2. Key lookup on literal dict or dict-typed parameter
            if not self._catches("KeyError"):
                if isinstance(node.value, ast.Name) and isinstance(idx, ast.Constant) and isinstance(idx.value, str):
                    if (val_dump, ast.dump(idx)) not in self.key_guarded:
                        keys = self._lookup_dict_keys(node.value.id)
                        if keys is not None and idx.value not in keys:
                            self._err("KeyError", repr(idx.value), node)
                        elif node.value.id in self.param_dict_stack[-1]:
                            self._err("KeyError", repr(idx.value), node)
        self.generic_visit(node)

    def visit_Import(self, node):
        if not self._catches("ModuleNotFoundError"):
            for alias in node.names:
                mod_name = alias.name.split('.')[0]
                if mod_name not in sys.builtin_module_names and mod_name not in sys.modules:
                    try:
                        spec = importlib.util.find_spec(mod_name)
                    except (ImportError, ValueError, AttributeError):
                        spec = None
                    if spec is None:
                        self._err("ModuleNotFoundError", f"No module named '{alias.name}'", node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if not self._catches("ModuleNotFoundError"):
            if node.module:
                mod_name = node.module.split('.')[0]
                if mod_name not in sys.builtin_module_names and mod_name not in sys.modules:
                    try:
                        spec = importlib.util.find_spec(mod_name)
                    except (ImportError, ValueError, AttributeError):
                        spec = None
                    if spec is None:
                        self._err("ModuleNotFoundError", f"No module named '{node.module}'", node)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if not self._catches("AttributeError"):
            val_dump = ast.dump(node.value)
            guarded = ((val_dump, "*") in self.attr_guarded
                       or (val_dump, node.attr) in self.attr_guarded)
            if not guarded:
                obj_t = self._infer_type(node.value)
                if obj_t in _TYPE_ATTRS and node.attr not in _TYPE_ATTRS[obj_t]:
                    self._err("AttributeError",
                              f"'{obj_t}' object has no attribute '{node.attr}'",
                              node)
                elif obj_t == "Any" and node.attr in _STRICT_ANY_METHODS:
                    self._err("AttributeError",
                              f"'Any' object may have no attribute '{node.attr}'",
                              node)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and not node.keywords:
            fn = node.func.id
            # 1. Invalid literal conversion: int("not-a-number") / float("abc")
            if fn in ("int", "float") and len(node.args) in (1, 2) \
                    and not self._catches("ValueError") and not self.value_guarded:
                arg0 = node.args[0]
                if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                    try:
                        if fn == "int" and len(node.args) == 2:
                            base = _eval_int_const(node.args[1])
                            if base is not None:
                                int(arg0.value, base)
                        else:
                            (int if fn == "int" else float)(arg0.value)
                    except ValueError as exc:
                        self._err("ValueError", str(exc), node)

            # 2. Wrong argument types to common builtins (TypeError)
            if not self._catches("TypeError"):
                if fn == "len" and len(node.args) == 1:
                    t = self._infer_type(node.args[0])
                    if t in _NON_SIZED_TYPES:
                        self._err("TypeError", f"object of type '{t}' has no len()", node)
                elif fn == "abs" and len(node.args) == 1:
                    t = self._infer_type(node.args[0])
                    if t in _NON_NUMERIC_TYPES:
                        self._err("TypeError", f"bad operand type for abs(): '{t}'", node)
                elif fn == "range" and 1 <= len(node.args) <= 3:
                    for arg in node.args:
                        t = self._infer_type(arg)
                        if t in _NON_INT_INDEX_TYPES:
                            self._err("TypeError", f"'{t}' object cannot be interpreted as an integer", node)
                            break
                elif fn == "ord" and len(node.args) == 1:
                    t = self._infer_type(node.args[0])
                    if t in _NON_SIZED_TYPES or t in ("list", "dict", "set", "tuple"):
                        self._err("TypeError", f"ord() expected string of length 1, but {t} found", node)
                elif fn == "chr" and len(node.args) == 1:
                    t = self._infer_type(node.args[0])
                    if t in _NON_INT_INDEX_TYPES:
                        self._err("TypeError", f"'{t}' object cannot be interpreted as an integer", node)
                elif fn in self.func_arity and not any(isinstance(a, ast.Starred) for a in node.args):
                    min_req, max_req, pnames = self.func_arity[fn]
                    given = len(node.args)
                    if given < min_req:
                        missing = [repr(p) for p in pnames[given:min_req]]
                        diff = min_req - given
                        self._err(
                            "TypeError",
                            f"{fn}() missing {diff} required positional argument{'s' if diff > 1 else ''}: {', '.join(missing)}",
                            node,
                        )
                    elif given > max_req:
                        self._err(
                            "TypeError",
                            f"{fn}() takes {max_req} positional argument{'s' if max_req != 1 else ''} but {given} were given",
                            node,
                        )
        self.generic_visit(node)

    def visit_Compare(self, node):
        if len(node.ops) == 1 and len(node.comparators) == 1:
            op = node.ops[0]
            comp = node.comparators[0]
            # 1. Fixable LogicalError: using 'is' / 'is not' with a literal value (str, int, float, etc.)
            if isinstance(op, (ast.Is, ast.IsNot)):
                is_non_singleton_lit = (
                    (isinstance(comp, ast.Constant) and comp.value is not None and not isinstance(comp.value, bool))
                    or isinstance(comp, (ast.List, ast.Dict, ast.Set, ast.Tuple))
                )
                if is_non_singleton_lit:
                    op_word = "is not" if isinstance(op, ast.IsNot) else "is"
                    fix_op = "!=" if isinstance(op, ast.IsNot) else "=="
                    self._err(
                        "LogicalError",
                        f"identity operator '{op_word}' used with a literal value (checks memory address instead of equality; use '{fix_op}')",
                        node,
                    )
            # 2. Ambiguous LogicalError: comparing a variable to itself (e.g. x == x or x != x)
            elif isinstance(op, (ast.Eq, ast.NotEq, ast.Lt, ast.Gt, ast.LtE, ast.GtE)):
                if isinstance(node.left, ast.Name) and isinstance(comp, ast.Name) and node.left.id == comp.id:
                    self._err(
                        "LogicalError",
                        f"self-comparison on variable '{node.left.id}' always evaluates to a constant boolean (ambiguous comparison target)",
                        node,
                    )
        self.generic_visit(node)

    def visit_Assert(self, node):
        # Fixable LogicalError: assert (cond, "msg") is a non-empty tuple and is ALWAYS True
        if isinstance(node.test, ast.Tuple) and len(node.test.elts) >= 2:
            self._err(
                "LogicalError",
                "assertion on a non-empty tuple 'assert (condition, message)' is always True and never fails",
                node,
            )
        self.generic_visit(node)


def static_check(code):
    """Returns a list of IR-shaped error dicts. Raises SyntaxError if unparseable."""
    tree = ast.parse(code)
    checker = StaticChecker(tree)
    checker.visit(tree)
    return checker.errors
