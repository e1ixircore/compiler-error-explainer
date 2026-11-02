# static_analyzer.py
import ast, builtins, difflib

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


class StaticChecker(ast.NodeVisitor):
    def __init__(self, tree):
        # Scope stack = the symbol table. Index 0 = builtins, 1 = module globals.
        self.scopes = [set(dir(builtins)), bound_names(tree.body)]
        self.errors = []
        # Denominators proven non-zero by an ENCLOSING guard (`b != 0`).
        # This is a tiny path-sensitive analysis: facts hold only inside the guarded branch.
        self.guarded = set()

    def _err(self, etype, msg, node, **extra):
        self.errors.append({"error_type": etype, "error_message": msg,
                            "line_number": node.lineno,
                            "column": node.col_offset, **extra})

    # --- scopes -------------------------------------------------------
    def _function(self, node):
        for d in node.decorator_list: self.visit(d)
        a = node.args
        for d in a.defaults + [k for k in a.kw_defaults if k]: self.visit(d)
        params = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
        params |= {x.arg for x in (a.vararg, a.kwarg) if x}
        self.scopes.append(params | bound_names(node.body))
        for s in node.body: self.visit(s)
        self.scopes.pop()
    visit_FunctionDef = visit_AsyncFunctionDef = _function

    def visit_Lambda(self, node):
        a = node.args
        params = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
        self.scopes.append(params)
        self.visit(node.body)
        self.scopes.pop()

    def visit_ClassDef(self, node):
        self.scopes.append(bound_names(node.body))
        for s in node.body: self.visit(s)
        self.scopes.pop()

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

    def _visit_guarded(self, test, body, orelse):
        # The guard is true ONLY in `body`; in `orelse` it is not known, so it is removed.
        g = self._nonzero_guard(test)
        added = g is not None and g not in self.guarded
        self.visit(test)
        if added: self.guarded.add(g)
        for n in body: self.visit(n)
        if added: self.guarded.discard(g)
        for n in orelse: self.visit(n)

    def visit_IfExp(self, node):          # a / b if b != 0 else 0
        self._visit_guarded(node.test, [node.body], [node.orelse])

    def visit_If(self, node):             # if b != 0: ... a / b ...
        self._visit_guarded(node.test, node.body, node.orelse)

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
        # Constant folding catches obvious type mismatches without running code.
        if isinstance(node.op, ast.Add) and isinstance(l, ast.Constant) \
                and isinstance(r, ast.Constant):
            tl, tr = type(l.value), type(r.value)
            if tl is not tr and str in (tl, tr) and {tl, tr} <= {str, int, float}:
                self._err("TypeError",
                          f'can only concatenate str (not "{(tr if tl is str else tl).__name__}") to str',
                          node)
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) \
                and isinstance(r, ast.Constant) and r.value == 0 \
                and ast.dump(r) not in self.guarded:      # skip if an enclosing guard covers it
            self._err("ZeroDivisionError", "division by zero", node)
        self.generic_visit(node)


def static_check(code):
    """Returns a list of IR-shaped error dicts. Raises SyntaxError if unparseable."""
    tree = ast.parse(code)
    checker = StaticChecker(tree)
    checker.visit(tree)
    return checker.errors