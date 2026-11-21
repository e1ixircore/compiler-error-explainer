"""
cst_patcher.py
==============
Concrete Syntax Tree (CST) code mutation and patch application engine powered by LibCST.

Replaces fragile string slicing, regex line replacements, and indentation guessing
with lossless CST transformations that preserve:
  - inline, leading, and trailing comments
  - multi-line expressions and parenthesized continuations
  - original and mixed whitespace / indentation (tabs or spaces)
  - exact formatting outside the mutated AST/CST node
"""

from __future__ import annotations

import ast
import difflib
import re
import sys
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

import libcst as cst
from libcst.metadata import CodeRange, MetadataWrapper, PositionProvider

try:
    from word2number import w2n
except ImportError:
    w2n = None


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IMPORTABLE_STDLIB: Set[str] = {
    "math", "random", "sys", "json", "time", "datetime", "re", "os",
    "string", "statistics", "collections", "itertools", "functools",
}

STDLIB_MODULES: Set[str] = set(getattr(sys, "stdlib_module_names", ())) or (
    IMPORTABLE_STDLIB | {"csv", "tkinter", "queue", "configparser", "threading"}
)

LITERAL_ALIASES: Dict[str, str] = {
    "true": "True",
    "false": "False",
    "null": "None",
    "nil": "None",
    "none": "None",
}

STR_METHODS: Set[str] = {
    "upper", "lower", "strip", "lstrip", "rstrip", "split", "rsplit", "splitlines",
    "startswith", "endswith", "replace", "title", "capitalize", "casefold",
    "isdigit", "isalpha", "isalnum", "isnumeric", "isspace", "isupper", "islower",
    "swapcase", "zfill", "center", "ljust", "rjust",
}

TYPE_DEFAULTS: Dict[str, str] = {
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

PURE_FUNCS: Set[str] = {"len", "abs", "int", "float", "str", "sum", "min", "max", "round"}


# ---------------------------------------------------------------------------
# CST Utility Helpers
# ---------------------------------------------------------------------------

from ir_generator import cached_ast_parse

_SLICE_LINE_THRESHOLD = 120


def parse_cst(code: str) -> Optional[cst.Module]:
    """Parse Python source into a lossless LibCST Module, or None on syntax error."""
    try:
        return cst.parse_module(code)
    except (cst.ParserSyntaxError, Exception):
        return None


def _stmt_line_span(stmt: ast.stmt) -> Tuple[int, int]:
    """Return 1-based inclusive (start_line, end_line) for a top-level AST statement, including decorators."""
    start = getattr(stmt, "lineno", 1)
    decs = getattr(stmt, "decorator_list", None)
    if decs:
        start = min(start, *(getattr(d, "lineno", start) for d in decs))
    end = getattr(stmt, "end_lineno", None) or start
    return start, end


def _find_top_level_span(code: str, target_line: int) -> Optional[Tuple[int, int]]:
    """Locate the 1-based inclusive line span of the top-level statement covering `target_line`."""
    tree = cached_ast_parse(code)
    if tree is None:
        return None
    for stmt in tree.body:
        start, end = _stmt_line_span(stmt)
        if start <= target_line <= end:
            return start, end
    return None


def _run_transformer(code: str, transformer: cst.CSTTransformer) -> Tuple[str, bool]:
    """Run a PositionProvider-aware CSTTransformer on `code`. Returns (new_code, changed).
    For large files (>120 lines), uses C-speed `ast.parse` to isolate only the enclosing
    top-level statement so LibCST MetadataWrapper only processes tens of lines instead of thousands."""
    target_line = getattr(transformer, "target_line", None)
    if isinstance(target_line, int) and code.count("\n") > _SLICE_LINE_THRESHOLD:
        span = _find_top_level_span(code, target_line)
        if span is not None:
            s_start, s_end = span
            lines = code.splitlines(keepends=True)
            if 1 <= s_start <= s_end <= len(lines):
                slice_code = "".join(lines[s_start - 1 : s_end])
                mod = parse_cst(slice_code)
                if mod is not None:
                    orig_target = transformer.target_line
                    transformer.target_line = orig_target - s_start + 1
                    try:
                        wrapper = MetadataWrapper(mod)
                        new_mod = wrapper.visit(transformer)
                        new_slice = new_mod.code
                    except Exception:
                        return code, False
                    finally:
                        transformer.target_line = orig_target
                    if new_slice == slice_code:
                        return code, False
                    new_code = "".join(lines[: s_start - 1]) + new_slice + "".join(lines[s_end:])
                    return new_code, (new_code != code)

    mod = parse_cst(code)
    if mod is None:
        return code, False
    try:
        wrapper = MetadataWrapper(mod)
        new_mod = wrapper.visit(transformer)
        new_code = new_mod.code
        return new_code, (new_code != code)
    except Exception:
        return code, False


def _covers_line(pos: Optional[CodeRange], target_line: int) -> bool:
    if pos is None:
        return False
    return pos.start.line <= target_line <= pos.end.line


def _is_zero_literal(node: cst.BaseExpression) -> bool:
    """Return True if CST expression is numeric literal 0 or 0.0 (including +0 / -0)."""
    if isinstance(node, cst.UnaryOperation) and isinstance(node.operator, (cst.Plus, cst.Minus)):
        node = node.expression
    if isinstance(node, cst.Integer):
        try:
            return int(node.value, 0) == 0
        except ValueError:
            return False
    if isinstance(node, cst.Float):
        try:
            return float(node.value) == 0.0
        except ValueError:
            return False
    return False


def _is_strish_cst(node: cst.BaseExpression) -> bool:
    """Return True if CST expression clearly evaluates to a str."""
    if isinstance(node, (cst.SimpleString, cst.FormattedString, cst.ConcatenatedString)):
        return True
    if isinstance(node, cst.Call):
        if isinstance(node.func, cst.Name) and node.func.value == "str":
            return True
        if (
            isinstance(node.func, cst.Attribute)
            and node.func.attr.value in ("format", "join", "strip", "upper", "lower", "title")
            and _is_strish_cst(node.func.value)
        ):
            return True
    if isinstance(node, cst.BinaryOperation) and isinstance(node.operator, cst.Add):
        return _is_strish_cst(node.left) or _is_strish_cst(node.right)
    return False


def _is_pure_cst(node: cst.BaseExpression) -> bool:
    """True if evaluating `node` twice has no side effects."""
    if isinstance(node, (cst.Name, cst.Integer, cst.Float, cst.SimpleString)):
        return True
    if isinstance(node, cst.Attribute):
        return _is_pure_cst(node.value)
    if isinstance(node, cst.Subscript):
        if not _is_pure_cst(node.value):
            return False
        for el in node.slice:
            if isinstance(el.slice, cst.Index):
                if not _is_pure_cst(el.slice.value):
                    return False
            else:
                return False
        return True
    if isinstance(node, cst.UnaryOperation):
        return _is_pure_cst(node.expression)
    if isinstance(node, cst.BinaryOperation):
        return _is_pure_cst(node.left) and _is_pure_cst(node.right)
    if (
        isinstance(node.func if isinstance(node, cst.Call) else None, cst.Name)
        and isinstance(node, cst.Call)
        and node.func.value in PURE_FUNCS
        and all(a.keyword is None for a in node.args)
    ):
        return all(_is_pure_cst(a.value) for a in node.args)
    return False


def _wrap_call(func_name: str, expr: cst.BaseExpression) -> cst.Call:
    """Wrap `expr` in `func_name(expr)` cleanly on CST."""
    return cst.Call(
        func=cst.Name(func_name),
        args=[cst.Arg(value=expr)],
    )


def _quoted(msg: str) -> str:
    m = re.search(r"'([^']+)'", msg or "")
    return m.group(1) if m else ""


def _stdlib_near(name: str) -> Optional[str]:
    cands = [m for m in STDLIB_MODULES if not m.startswith("_")]
    low = {m.lower(): m for m in cands}
    if name.lower() in low and low[name.lower()] != name:
        return low[name.lower()]
    if len(name) < 4 or name in STDLIB_MODULES:
        return None
    m = difflib.get_close_matches(name, cands, n=1, cutoff=0.8)
    return m[0] if m else None


def _module_has_import(module: cst.Module, mod_name: str) -> bool:
    for stmt in module.body:
        if isinstance(stmt, cst.SimpleStatementLine):
            for small in stmt.body:
                if isinstance(small, cst.Import):
                    for alias in small.names:
                        if isinstance(alias.name, cst.Name) and alias.name.value == mod_name:
                            return True
    return False


def _import_insert_index(module: cst.Module) -> int:
    """Compute CST body index for inserting a new top-level import (after docstring & __future__)."""
    idx = 0
    if module.body:
        first = module.body[0]
        if (
            isinstance(first, cst.SimpleStatementLine)
            and len(first.body) == 1
            and isinstance(first.body[0], cst.Expr)
            and isinstance(first.body[0].value, (cst.SimpleString, cst.ConcatenatedString))
        ):
            idx = 1
        for i, stmt in enumerate(module.body):
            if isinstance(stmt, cst.SimpleStatementLine):
                for small in stmt.body:
                    if (
                        isinstance(small, cst.ImportFrom)
                        and isinstance(small.module, cst.Name)
                        and small.module.value == "__future__"
                    ):
                        idx = max(idx, i + 1)
    return idx


def ensure_imports_cst(code: str, module_names: Sequence[str]) -> str:
    """Insert missing `import <mod>` statements directly into the CST Module body,
    preserving header comments, module docstrings, and __future__ imports."""
    if not module_names:
        return code

    # Fast path for large files: inspect imports & header span via C-speed ast.parse
    # and run LibCST only on the module header prefix.
    if code.count("\n") > _SLICE_LINE_THRESHOLD:
        try:
            tree = ast.parse(code)
        except Exception:
            return code
        existing: Set[str] = set()
        for stmt in tree.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    existing.add(alias.name)
        missing = [m for m in module_names if m not in existing]
        if not missing:
            return code
        idx = 0
        if tree.body:
            first = tree.body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                idx = 1
            for i, stmt in enumerate(tree.body):
                if isinstance(stmt, ast.ImportFrom) and stmt.module == "__future__":
                    idx = max(idx, i + 1)
        lines = code.splitlines(keepends=True)
        if idx < len(tree.body):
            _, prefix_end = _stmt_line_span(tree.body[idx])
        else:
            prefix_end = len(lines)
        prefix = "".join(lines[:prefix_end])
        suffix = "".join(lines[prefix_end:])
        mod = parse_cst(prefix)
        if mod is not None:
            cst_idx = _import_insert_index(mod)
            new_stmts: List[cst.BaseStatement] = [
                cst.SimpleStatementLine(
                    body=[cst.Import(names=[cst.ImportAlias(name=cst.Name(m))])]
                )
                for m in missing
            ]
            body = list(mod.body)
            if cst_idx < len(body):
                target = body[cst_idx]
                if hasattr(target, "leading_lines") and target.leading_lines and cst_idx == 0:
                    new_stmts[0] = new_stmts[0].with_changes(leading_lines=target.leading_lines)
                    body[cst_idx] = target.with_changes(leading_lines=())
            new_prefix = mod.with_changes(body=body[:cst_idx] + new_stmts + body[cst_idx:]).code
            if suffix and not new_prefix.endswith("\n"):
                new_prefix += "\n"
            return new_prefix + suffix

    mod = parse_cst(code)
    if mod is None:
        return code
    missing = [m for m in module_names if not _module_has_import(mod, m)]
    if not missing:
        return code
    idx = _import_insert_index(mod)
    new_stmts = [
        cst.SimpleStatementLine(
            body=[cst.Import(names=[cst.ImportAlias(name=cst.Name(m))])]
        )
        for m in missing
    ]
    body = list(mod.body)
    if idx < len(body):
        # Move any leading header comments on body[idx] to the first inserted import
        # so module header comments stay at the very top of the file.
        target = body[idx]
        if hasattr(target, "leading_lines") and target.leading_lines and idx == 0:
            new_stmts[0] = new_stmts[0].with_changes(leading_lines=target.leading_lines)
            body[idx] = target.with_changes(leading_lines=())
    new_body = body[:idx] + new_stmts + body[idx:]
    return mod.with_changes(body=new_body).code


# ---------------------------------------------------------------------------
# Functional Bug CST Transformers
# ---------------------------------------------------------------------------

class _LogicalIsToEqTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, target_line: int) -> None:
        self.target_line = target_line
        self.changed = False

    def leave_ComparisonTarget(
        self, original_node: cst.ComparisonTarget, updated_node: cst.ComparisonTarget
    ) -> cst.ComparisonTarget:
        if self.changed:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        op = updated_node.operator
        if isinstance(op, cst.IsNot):
            self.changed = True
            return updated_node.with_changes(
                operator=cst.NotEqual(
                    whitespace_before=op.whitespace_before,
                    whitespace_after=op.whitespace_after,
                )
            )
        if isinstance(op, cst.Is):
            self.changed = True
            return updated_node.with_changes(
                operator=cst.Equal(
                    whitespace_before=op.whitespace_before,
                    whitespace_after=op.whitespace_after,
                )
            )
        return updated_node


class _AssertTupleUnwrapTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, target_line: int) -> None:
        self.target_line = target_line
        self.changed = False

    def leave_Assert(
        self, original_node: cst.Assert, updated_node: cst.Assert
    ) -> cst.Assert:
        if self.changed:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        if updated_node.msg is None and isinstance(updated_node.test, cst.Tuple):
            elems = updated_node.test.elements
            if len(elems) >= 2:
                self.changed = True
                test_expr = elems[0].value
                msg_expr = elems[1].value
                # Always use single-line whitespace after the comma when unwrapping
                # a parenthesized tuple, since a bare newline outside () is invalid syntax.
                comma = cst.Comma(whitespace_after=cst.SimpleWhitespace(" "))
                return updated_node.with_changes(
                    test=test_expr,
                    comma=comma,
                    msg=msg_expr,
                    whitespace_after_assert=cst.SimpleWhitespace(" "),
                )
        return updated_node


class _ZeroDivisionTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, target_line: int, allow_dynamic_guard: bool = True) -> None:
        self.target_line = target_line
        self.allow_dynamic_guard = allow_dynamic_guard
        self.changed = False
        self.kind = ""
        self.denom_name = ""

    def leave_BinaryOperation(
        self, original_node: cst.BinaryOperation, updated_node: cst.BinaryOperation
    ) -> cst.BaseExpression:
        if self.changed:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        if not isinstance(updated_node.operator, (cst.Divide, cst.FloorDivide, cst.Modulo)):
            return updated_node
        if _is_zero_literal(updated_node.right):
            self.changed = True
            self.kind = (
                "floordiv" if isinstance(updated_node.operator, cst.FloorDivide)
                else "mod" if isinstance(updated_node.operator, cst.Modulo)
                else "div"
            )
            return updated_node.with_changes(right=cst.Integer("1"))
        if self.allow_dynamic_guard and _is_pure_cst(updated_node.right):
            self.changed = True
            self.kind = "dynamic"
            denom = updated_node.right
            self.denom_name = cst.Module([]).code_for_node(denom).strip()
            cond = cst.Comparison(
                left=denom,
                comparisons=[
                    cst.ComparisonTarget(
                        operator=cst.NotEqual(),
                        comparator=cst.Integer("0"),
                    )
                ],
            )
            return cst.IfExp(
                test=cond,
                body=updated_node,
                orelse=cst.Integer("0"),
                lpar=[cst.LeftParen()],
                rpar=[cst.RightParen()],
            )
        return updated_node


class _NameRenameTransformer(cst.CSTTransformer):
    """Rename `bad_name` -> `new_name` (or `self.<bad_name>`) on CST nodes covering `target_line`.
    Never touches attribute names (obj.bad), keyword argument names (f(bad=1)), comments, or strings."""
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, target_line: int, bad_name: str, new_name: str, add_self: bool = False) -> None:
        self.target_line = target_line
        self.bad_name = bad_name
        self.new_name = new_name
        self.add_self = add_self
        self.changed = False
        self._skip_name_ids: Set[int] = set()

    def visit_Attribute(self, node: cst.Attribute) -> Optional[bool]:
        # Do not rename the `.attr` part of `obj.attr`
        self._skip_name_ids.add(id(node.attr))
        return True

    def visit_Arg(self, node: cst.Arg) -> Optional[bool]:
        # Do not rename keyword parameter names in `func(bad=1)`
        if node.keyword is not None:
            self._skip_name_ids.add(id(node.keyword))
        return True

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.BaseExpression:
        if id(original_node) in self._skip_name_ids:
            return updated_node
        if original_node.value != self.bad_name:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        self.changed = True
        if self.add_self:
            return cst.Attribute(value=cst.Name("self"), attr=cst.Name(self.bad_name))
        return updated_node.with_changes(value=self.new_name)


class _InsertInitBeforeLineTransformer(cst.CSTTransformer):
    """Insert `<var> = <default>` statement right before the statement covering `target_line`
    (or before its enclosing loop if inside a loop), using CST block indentation."""
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, target_line: int, var_name: str, init_expr: str = "0") -> None:
        self.target_line = target_line
        self.var_name = var_name
        self.init_expr = init_expr
        self.changed = False

    def _maybe_insert_in_body(
        self, orig_body: Sequence[cst.BaseStatement], upd_body: Sequence[cst.BaseStatement]
    ) -> Tuple[List[cst.BaseStatement], bool]:
        if self.changed:
            return list(upd_body), False
        for i, orig_stmt in enumerate(orig_body):
            pos = self.get_metadata(PositionProvider, orig_stmt, None)
            if pos and pos.start.line == self.target_line:
                init_stmt = cst.parse_statement(f"{self.var_name} = {self.init_expr}\n")
                new_body = list(upd_body)
                new_body.insert(i, init_stmt)
                self.changed = True
                return new_body, True
        return list(upd_body), False

    def leave_IndentedBlock(
        self, original_node: cst.IndentedBlock, updated_node: cst.IndentedBlock
    ) -> cst.IndentedBlock:
        new_body, inserted = self._maybe_insert_in_body(original_node.body, updated_node.body)
        return updated_node.with_changes(body=new_body) if inserted else updated_node

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.Module:
        new_body, inserted = self._maybe_insert_in_body(original_node.body, updated_node.body)
        return updated_node.with_changes(body=new_body) if inserted else updated_node


class _TypeErrorCSTTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, target_line: int, msg: str, fn_return_type: Optional[str] = None) -> None:
        self.target_line = target_line
        self.msg = msg or ""
        self.fn_return_type = fn_return_type
        self.changed = False
        self.action_note = ""
        self._in_index_zone = 0

        self.cm = re.search(r"'(<=|>=|<|>)' not supported between instances of '(\w+)' and '(\w+)'", self.msg)
        self.am = re.search(r"unsupported operand type\(s\) for (\*\*|//|[-*/%]): '(\w+)' and '(\w+)'", self.msg)
        self.is_concat = (
            "concatenate" in self.msg
            or bool(re.search(r"for \+: '(int|float)' and 'str'", self.msg))
            or not self.msg
        )
        self.is_not_iter = "'int' object is not iterable" in self.msg
        self.is_float_idx = (
            "indices must be integers" in self.msg
            or "cannot be interpreted as an integer" in self.msg
            or "slice indices" in self.msg
        )
        self.is_no_len = "has no len()" in self.msg
        self.is_none_sub = "'NoneType' object is not subscriptable" in self.msg
        self.is_ret_mismatch = "return type mismatch" in self.msg
        self.is_ann_mismatch = "incompatible type in assignment" in self.msg

    def visit_Subscript(self, node: cst.Subscript) -> Optional[bool]:
        pos = self.get_metadata(PositionProvider, node, None)
        if self.is_float_idx and _covers_line(pos, self.target_line):
            self._in_index_zone += 1
        return True

    def leave_Subscript(
        self, original_node: cst.Subscript, updated_node: cst.Subscript
    ) -> cst.Subscript:
        pos = self.get_metadata(PositionProvider, original_node, None)
        if self.is_float_idx and _covers_line(pos, self.target_line):
            self._in_index_zone = max(0, self._in_index_zone - 1)
        if self.is_none_sub and not self.changed and _covers_line(pos, self.target_line):
            self.changed = True
            self.action_note = "Guarded potential NoneType container"
            guarded = cst.BooleanOperation(
                left=updated_node.value,
                operator=cst.Or(),
                right=cst.Dict([]),
                lpar=[cst.LeftParen()],
                rpar=[cst.RightParen()],
            )
            return updated_node.with_changes(value=guarded)
        return updated_node

    def visit_Call(self, node: cst.Call) -> Optional[bool]:
        pos = self.get_metadata(PositionProvider, node, None)
        if (
            self.is_float_idx
            and _covers_line(pos, self.target_line)
            and isinstance(node.func, cst.Name)
            and node.func.value == "range"
        ):
            self._in_index_zone += 1
        return True

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        pos = self.get_metadata(PositionProvider, original_node, None)
        if (
            self.is_float_idx
            and _covers_line(pos, self.target_line)
            and isinstance(original_node.func, cst.Name)
            and original_node.func.value == "range"
        ):
            self._in_index_zone = max(0, self._in_index_zone - 1)
        if (
            self.is_no_len
            and _covers_line(pos, self.target_line)
            and isinstance(updated_node.func, cst.Name)
            and updated_node.func.value == "len"
            and len(updated_node.args) == 1
        ):
            self.changed = True
            self.action_note = "Wrapped len() argument with str()"
            arg0 = updated_node.args[0]
            return updated_node.with_changes(
                args=[arg0.with_changes(value=_wrap_call("str", arg0.value))]
            )
        return updated_node

    def leave_For(self, original_node: cst.For, updated_node: cst.For) -> cst.For:
        if not self.is_not_iter:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node.iter, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        if not (
            isinstance(updated_node.iter, cst.Call)
            and isinstance(updated_node.iter.func, cst.Name)
            and updated_node.iter.func.value == "range"
        ):
            self.changed = True
            self.action_note = "Wrapped integer loop target in range()"
            return updated_node.with_changes(iter=_wrap_call("range", updated_node.iter))
        return updated_node

    def leave_BinaryOperation(
        self, original_node: cst.BinaryOperation, updated_node: cst.BinaryOperation
    ) -> cst.BinaryOperation:
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node

        # Float division inside subscript or range() -> integer floor division '//'
        if self.is_float_idx and self._in_index_zone > 0 and isinstance(updated_node.operator, cst.Divide):
            self.changed = True
            self.action_note = "Converted float division '/' to integer floor division '//'"
            op = updated_node.operator
            return updated_node.with_changes(
                operator=cst.FloorDivide(
                    whitespace_before=op.whitespace_before,
                    whitespace_after=op.whitespace_after,
                )
            )

        # String + non-string concatenation -> wrap non-string in str(...)
        if self.is_concat and isinstance(updated_node.operator, cst.Add):
            ls = _is_strish_cst(updated_node.left)
            rs = _is_strish_cst(updated_node.right)
            if ls != rs:
                self.changed = True
                self.action_note = "Wrapped non-string operand with str()"
                if ls:
                    return updated_node.with_changes(right=_wrap_call("str", updated_node.right))
                return updated_node.with_changes(left=_wrap_call("str", updated_node.left))

        # Arithmetic with string operand (e.g. '10' - 2)
        if self.am:
            sym, lt, rt = self.am.groups()
            op_map = {
                "-": cst.Subtract, "*": cst.Multiply, "/": cst.Divide,
                "//": cst.FloorDivide, "%": cst.Modulo, "**": cst.Power,
            }
            if op_map.get(sym) and isinstance(updated_node.operator, op_map[sym]):
                side = "left" if lt == "str" else "right" if rt == "str" else None
                if side:
                    target = updated_node.left if side == "left" else updated_node.right
                    repl = self._coerce_str_to_num(target)
                    if repl is not None:
                        self.changed = True
                        self.action_note = "Converted string operand to numeric value"
                        return (
                            updated_node.with_changes(left=repl)
                            if side == "left"
                            else updated_node.with_changes(right=repl)
                        )
        return updated_node

    def leave_Comparison(
        self, original_node: cst.Comparison, updated_node: cst.Comparison
    ) -> cst.Comparison:
        if not self.cm or len(updated_node.comparisons) != 1:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        sym, lt, rt = self.cm.groups()
        cmp_map = {
            "<": cst.LessThan, ">": cst.GreaterThan,
            "<=": cst.LessThanEqual, ">=": cst.GreaterThanEqual,
        }
        tgt = updated_node.comparisons[0]
        if cmp_map.get(sym) and isinstance(tgt.operator, cmp_map[sym]):
            side = "left" if lt == "str" else "right" if rt == "str" else None
            if side == "left":
                repl = self._coerce_str_to_num(updated_node.left)
                if repl is not None:
                    self.changed = True
                    self.action_note = "Converted string operand to numeric value"
                    return updated_node.with_changes(left=repl)
            elif side == "right":
                repl = self._coerce_str_to_num(tgt.comparator)
                if repl is not None:
                    self.changed = True
                    self.action_note = "Converted string operand to numeric value"
                    return updated_node.with_changes(
                        comparisons=[tgt.with_changes(comparator=repl)]
                    )
        return updated_node

    def leave_Return(self, original_node: cst.Return, updated_node: cst.Return) -> cst.Return:
        if not self.is_ret_mismatch or updated_node.value is None:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        rm = re.search(r"expected '([^']+)', got '([^']+)'", self.msg)
        exp = rm.group(1).split(" | ")[0].strip() if rm else None
        if not exp:
            return updated_node
        repl = self._coerce_for_type(updated_node.value, exp)
        if repl is not None:
            self.changed = True
            self.action_note = f"Converted return value to match '{exp}'"
            return updated_node.with_changes(value=repl)
        return updated_node

    def leave_AnnAssign(
        self, original_node: cst.AnnAssign, updated_node: cst.AnnAssign
    ) -> cst.AnnAssign:
        if not self.is_ann_mismatch or updated_node.value is None:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        rm = re.search(r"assignment to '([^']+)': expected '([^']+)', got '([^']+)'", self.msg)
        if not rm:
            return updated_node
        _, exp, got = rm.groups()
        exp = exp.split(" | ")[0].strip()
        got = got.split(" | ")[0].strip()
        if self.fn_return_type == got and got in TYPE_DEFAULTS:
            self.changed = True
            self.action_note = f"Updated type annotation to '{got}'"
            return updated_node.with_changes(
                annotation=updated_node.annotation.with_changes(annotation=cst.Name(got))
            )
        repl = self._coerce_for_type(updated_node.value, exp)
        if repl is not None:
            self.changed = True
            self.action_note = f"Converted assigned value to match '{exp}'"
            return updated_node.with_changes(value=repl)
        return updated_node

    @staticmethod
    def _coerce_str_to_num(node: cst.BaseExpression) -> Optional[cst.BaseExpression]:
        if isinstance(node, cst.SimpleString):
            try:
                val = ast.literal_eval(node.value)
            except Exception:
                return None
            if isinstance(val, str) and re.fullmatch(r"\s*-?\d+(\.\d+)?\s*", val):
                stripped = val.strip()
                return cst.parse_expression(stripped)
            return None
        return _wrap_call("int", node)

    @staticmethod
    def _coerce_for_type(node: cst.BaseExpression, exp: str) -> Optional[cst.BaseExpression]:
        if exp == "str":
            return _wrap_call("str", node)
        if isinstance(node, cst.SimpleString) and exp in ("int", "float"):
            try:
                val = ast.literal_eval(node.value)
            except Exception:
                return None
            if isinstance(val, str) and re.fullmatch(r"\s*-?\d+(\.\d+)?\s*", val):
                num = str(int(float(val))) if exp == "int" else str(float(val))
                return cst.parse_expression(num)
        return None


class _IndexErrorCSTTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, target_line: int) -> None:
        self.target_line = target_line
        self.changed = False
        self.action_note = ""

    def leave_Subscript(
        self, original_node: cst.Subscript, updated_node: cst.Subscript
    ) -> cst.BaseExpression:
        if self.changed:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        if len(updated_node.slice) != 1 or not isinstance(updated_node.slice[0].slice, cst.Index):
            return updated_node

        target = updated_node.value
        idx_expr = updated_node.slice[0].slice.value
        tmp = cst.Module([])
        target_code = tmp.code_for_node(target).strip()

        # Pattern 1: arr[len(arr)] -> arr[len(arr) - 1]
        if (
            isinstance(idx_expr, cst.Call)
            and isinstance(idx_expr.func, cst.Name)
            and idx_expr.func.value == "len"
            and len(idx_expr.args) == 1
            and tmp.code_for_node(idx_expr.args[0].value).strip() == target_code
        ):
            self.changed = True
            self.action_note = f"Fixed off-by-one index '{target_code}[len({target_code})]' -> '{target_code}[len({target_code}) - 1]'"
            new_idx = cst.BinaryOperation(
                left=idx_expr,
                operator=cst.Subtract(),
                right=cst.Integer("1"),
            )
            new_elem = updated_node.slice[0].with_changes(slice=cst.Index(value=new_idx))
            return updated_node.with_changes(slice=[new_elem])

        # Pattern 2: arr[i] -> (arr[i] if i < len(arr) else arr[-1])
        if _is_pure_cst(target) and _is_pure_cst(idx_expr):
            self.changed = True
            idx_code = tmp.code_for_node(idx_expr).strip()
            self.action_note = f"Guarded list access against out-of-range index '{idx_code}'"
            len_call = _wrap_call("len", target)
            if isinstance(idx_expr, cst.Integer):
                cond = cst.Comparison(
                    left=len_call,
                    comparisons=[cst.ComparisonTarget(operator=cst.GreaterThan(), comparator=idx_expr)],
                )
            else:
                cond = cst.Comparison(
                    left=idx_expr,
                    comparisons=[cst.ComparisonTarget(operator=cst.LessThan(), comparator=len_call)],
                )
            fallback = cst.Subscript(
                value=target,
                slice=[cst.SubscriptElement(slice=cst.Index(
                    value=cst.UnaryOperation(operator=cst.Minus(), expression=cst.Integer("1"))
                ))],
            )
            return cst.IfExp(
                test=cond,
                body=updated_node,
                orelse=fallback,
                lpar=[cst.LeftParen()],
                rpar=[cst.RightParen()],
            )
        return updated_node


class _KeyErrorCSTTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, target_line: int, allow_direct_get: bool = False) -> None:
        self.target_line = target_line
        self.allow_direct_get = allow_direct_get
        self.changed = False
        self.action_note = ""
        self._assign_target_ids: Set[int] = set()

    def visit_AssignTarget(self, node: cst.AssignTarget) -> Optional[bool]:
        self._assign_target_ids.add(id(node.target))
        return True

    def leave_AugAssign(
        self, original_node: cst.AugAssign, updated_node: cst.AugAssign
    ) -> cst.BaseSmallStatement:
        if self.changed:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        if not isinstance(updated_node.target, cst.Subscript):
            return updated_node
        sub = updated_node.target
        if len(sub.slice) != 1 or not isinstance(sub.slice[0].slice, cst.Index):
            return updated_node
        op_map = {
            cst.AddAssign: (cst.Add, "0"),
            cst.SubtractAssign: (cst.Subtract, "0"),
            cst.MultiplyAssign: (cst.Multiply, "1"),
        }
        op_info = op_map.get(type(updated_node.operator))
        if not op_info:
            return updated_node
        bin_op_cls, default_str = op_info
        key_expr = sub.slice[0].slice.value
        if not (_is_pure_cst(sub.value) and _is_pure_cst(key_expr)):
            return updated_node
        if isinstance(updated_node.value, cst.SimpleString):
            default_str = "''"
        elif isinstance(updated_node.value, cst.List):
            default_str = "[]"
        get_call = cst.Call(
            func=cst.Attribute(value=sub.value, attr=cst.Name("get")),
            args=[cst.Arg(value=key_expr), cst.Arg(value=cst.parse_expression(default_str))],
        )
        rhs = cst.BinaryOperation(left=get_call, operator=bin_op_cls(), right=updated_node.value)
        self.changed = True
        self.action_note = "Converted counter subscript update to safe .get() default"
        return cst.Assign(targets=[cst.AssignTarget(target=sub)], value=rhs)

    def leave_Subscript(
        self, original_node: cst.Subscript, updated_node: cst.Subscript
    ) -> cst.BaseExpression:
        if not self.allow_direct_get or self.changed:
            return updated_node
        if id(original_node) in self._assign_target_ids:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        if len(updated_node.slice) != 1 or not isinstance(updated_node.slice[0].slice, cst.Index):
            return updated_node
        key_expr = updated_node.slice[0].slice.value
        if isinstance(key_expr, cst.SimpleString):
            self.changed = True
            self.action_note = f"Converted direct dictionary lookup to safe .get({key_expr.value})"
            return cst.Call(
                func=cst.Attribute(value=updated_node.value, attr=cst.Name("get")),
                args=[cst.Arg(value=key_expr)],
            )
        return updated_node


class _AttributeErrorCSTTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, target_line: int, msg: str) -> None:
        self.target_line = target_line
        self.msg = msg or ""
        self.changed = False
        self.action_note = ""
        m = re.search(r"attribute '([^']+)'", self.msg)
        self.attr_name = m.group(1) if m else None

    def leave_Attribute(
        self, original_node: cst.Attribute, updated_node: cst.Attribute
    ) -> cst.Attribute:
        if self.changed:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        if "'set' object has no attribute 'append'" in self.msg and updated_node.attr.value == "append":
            self.changed = True
            self.action_note = "Replaced set.append() with set.add()"
            return updated_node.with_changes(attr=cst.Name("add"))
        if "'list' object has no attribute 'add'" in self.msg and updated_node.attr.value == "add":
            self.changed = True
            self.action_note = "Replaced list.add() with list.append()"
            return updated_node.with_changes(attr=cst.Name("append"))
        if (
            "'NoneType' object has no attribute" not in self.msg
            and (self.attr_name is None or updated_node.attr.value == self.attr_name)
            and updated_node.attr.value in STR_METHODS
        ):
            self.changed = True
            self.action_note = f"Wrapped value with str() before calling .{updated_node.attr.value}()"
            return updated_node.with_changes(value=_wrap_call("str", updated_node.value))
        return updated_node

    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.BaseExpression:
        if self.changed or "'NoneType' object has no attribute" not in self.msg:
            return updated_node
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        if isinstance(updated_node.func, cst.Attribute) and _is_pure_cst(updated_node.func.value):
            target = updated_node.func.value
            self.changed = True
            self.action_note = f"Added NoneType guard before calling .{updated_node.func.attr.value}()"
            cond = cst.Comparison(
                left=target,
                comparisons=[cst.ComparisonTarget(operator=cst.IsNot(), comparator=cst.Name("None"))],
            )
            return cst.IfExp(
                test=cond,
                body=updated_node,
                orelse=cst.SimpleString("''"),
                lpar=[cst.LeftParen()],
                rpar=[cst.RightParen()],
            )
        return updated_node


class _ValueErrorCSTTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, target_line: int, msg: str) -> None:
        self.target_line = target_line
        self.msg = msg or ""
        self.floaty = bool(re.search(r"'[-+]?\d+\.\d+'", self.msg))
        self.changed = False

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        if not (
            isinstance(updated_node.func, cst.Name)
            and updated_node.func.value in ("int", "float")
            and len(updated_node.args) == 1
            and updated_node.args[0].keyword is None
        ):
            return updated_node
        fn = updated_node.func.value
        arg0 = updated_node.args[0]
        val_node = arg0.value
        if isinstance(val_node, cst.SimpleString):
            try:
                raw = ast.literal_eval(val_node.value)
            except Exception:
                return updated_node
            if not isinstance(raw, str):
                return updated_node
            try:
                (int if fn == "int" else float)(raw)
                return updated_node
            except ValueError:
                pass
            if fn == "int" and w2n is not None:
                try:
                    number = w2n.word_to_num(raw)
                    self.changed = True
                    return updated_node.with_changes(
                        args=[arg0.with_changes(value=cst.Integer(str(number)))]
                    )
                except ValueError:
                    pass
        if fn == "int" and self.floaty:
            self.changed = True
            return updated_node.with_changes(
                args=[arg0.with_changes(value=_wrap_call("float", val_node))]
            )
        return updated_node


class _ModuleNotFoundCSTTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, target_line: int, top_mod: str, near_mod: str) -> None:
        self.target_line = target_line
        self.top_mod = top_mod
        self.near_mod = near_mod
        self.changed = False

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        new_aliases: List[cst.ImportAlias] = []
        for alias in updated_node.names:
            if isinstance(alias.name, cst.Name) and alias.name.value == self.top_mod:
                bound = alias.asname or cst.AsName(name=cst.Name(self.top_mod))
                new_aliases.append(alias.with_changes(name=cst.Name(self.near_mod), asname=bound))
                self.changed = True
            else:
                new_aliases.append(alias)
        return updated_node.with_changes(names=new_aliases) if self.changed else updated_node

    def leave_ImportFrom(
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> cst.ImportFrom:
        pos = self.get_metadata(PositionProvider, original_node, None)
        if not _covers_line(pos, self.target_line):
            return updated_node
        if not updated_node.relative and isinstance(updated_node.module, cst.Name) and updated_node.module.value == self.top_mod:
            self.changed = True
            return updated_node.with_changes(module=cst.Name(self.near_mod))
        return updated_node


# ---------------------------------------------------------------------------
# Public Functional CST Repair Entry Point
# ---------------------------------------------------------------------------

def apply_functional_cst_fix(
    code: str,
    error_type: str,
    error_message: str,
    line_no: int,
    suggestion: Optional[str] = None,
    error_variable: Optional[str] = None,
    enclosing_class: Optional[str] = None,
    class_attributes: Optional[Set[str]] = None,
    local_symbols: Optional[Set[str]] = None,
    fn_return_type: Optional[str] = None,
    contextual: bool = False,
) -> Tuple[str, str, str]:
    """
    Perform a direct CST mutation for a Python functional/static/runtime error.
    Returns `(new_code, action_summary, explanation)`.
    If no CST rule applies (or code is unparseable), returns `(code, "", "")`.
    """
    if not line_no or line_no < 1:
        return code, "", ""
    emsg = error_message or ""

    # 1. LogicalError
    if error_type == "LogicalError":
        if "identity operator" in emsg:
            tr = _LogicalIsToEqTransformer(line_no)
            new_code, changed = _run_transformer(code, tr)
            if changed:
                return (
                    new_code,
                    f"L{line_no} [CST_FIX]: Replaced identity check 'is' with value equality '=='",
                    f"Mistake: Used 'is' to compare with a literal value on line {line_no}.\n"
                    "Reason: 'is' checks memory identity rather than value equality.\n"
                    "Fix: Replaced with '==' / '!='.",
                )
        elif "non-empty tuple" in emsg:
            tr = _AssertTupleUnwrapTransformer(line_no)
            new_code, changed = _run_transformer(code, tr)
            if changed:
                return (
                    new_code,
                    f"L{line_no} [CST_FIX]: Removed tuple parentheses around assert statement",
                    f"Mistake: Wrote assert(condition, message) as a tuple on line {line_no}.\n"
                    "Reason: A non-empty tuple is always True in Python, so the assert never triggers.\n"
                    "Fix: Removed outer parentheses.",
                )

    # 2. ZeroDivisionError
    elif error_type == "ZeroDivisionError" or "division by zero" in emsg:
        tr = _ZeroDivisionTransformer(line_no, allow_dynamic_guard=contextual)
        new_code, changed = _run_transformer(code, tr)
        if changed:
            if tr.kind == "dynamic":
                return (
                    new_code,
                    f"L{line_no} [CST_FIX]: Guarded dynamic division by zero for '{tr.denom_name}'",
                    f"Mistake: Variable '{tr.denom_name}' evaluated to zero on line {line_no}.\n"
                    "Reason: Dividing by a variable whose runtime value is 0 causes a ZeroDivisionError.\n"
                    f"Fix: Added safety guard: if {tr.denom_name} != 0 else 0.",
                )
            return (
                new_code,
                f"L{line_no} [CST_FIX]: Replaced division by zero with safe divisor (1)",
                f"Mistake: The program tried to divide by zero on line {line_no}.\n"
                "Reason: In arithmetic, division by zero is undefined.\n"
                "Fix: Replaced zero divisor with 1.",
            )

    # 3. NameError / UnboundLocalError
    elif error_type in ("NameError", "UnboundLocalError"):
        bad = error_variable or _quoted(emsg)
        if not bad:
            m_unbound = re.search(r"variable '([^']+)'", emsg)
            if m_unbound:
                bad = m_unbound.group(1)
        if bad:
            # 3A. Missing `self.` inside class method
            if enclosing_class and class_attributes and bad in class_attributes:
                tr = _NameRenameTransformer(line_no, bad, bad, add_self=True)
                new_code, changed = _run_transformer(code, tr)
                if changed:
                    return (
                        new_code,
                        f"L{line_no} [CST_FIX]: Added missing 'self.' to class attribute 'self.{bad}'",
                        f"Mistake: Referenced '{bad}' without 'self.' on line {line_no}.\n"
                        "Reason: In Python classes, instance attributes must be accessed through 'self'.\n"
                        f"Fix: Changed to 'self.{bad}'.",
                    )
            # 3B. Forgotten stdlib import
            if bad in IMPORTABLE_STDLIB:
                new_code = ensure_imports_cst(code, [bad])
                if new_code != code:
                    return (
                        new_code,
                        f"L1 [CST_FIX]: Added missing forgotten import 'import {bad}'",
                        f"Mistake: Standard library '{bad}' used on line {line_no} before being imported.\n"
                        "Reason: Python requires an import statement before using standard library modules.\n"
                        f"Fix: Added 'import {bad}' at the top of the file.",
                    )
            # 3C. Foreign literal aliases (true/false/null)
            if bad.lower() in LITERAL_ALIASES and bad not in LITERAL_ALIASES.values():
                right = LITERAL_ALIASES[bad.lower()]
                tr = _NameRenameTransformer(line_no, bad, right)
                new_code, changed = _run_transformer(code, tr)
                if changed:
                    return (
                        new_code,
                        f"L{line_no} [CST_FIX]: Replaced '{bad}' with Python literal '{right}'",
                        f"Mistake: '{bad}' is not a Python keyword on line {line_no}.\n"
                        "Reason: Python spells True, False, and None with capital first letters.\n"
                        f"Fix: Replaced '{bad}' with '{right}'.",
                    )
            # 3D. Typo correction from suggestion or local_symbols
            near = suggestion
            if not near and local_symbols:
                cands = [s for s in local_symbols if s != bad]
                matches = difflib.get_close_matches(bad, cands, n=1, cutoff=0.72)
                if matches:
                    near = matches[0]
            if near and near != bad:
                tr = _NameRenameTransformer(line_no, bad, near)
                new_code, changed = _run_transformer(code, tr)
                if changed:
                    return (
                        new_code,
                        f"L{line_no} [CST_FIX]: Corrected variable typo '{bad}' -> '{near}'",
                        f"Mistake: Name '{bad}' is not defined on line {line_no}.\n"
                        f"Reason: It is a typo of the existing variable '{near}'.\n"
                        f"Fix: Renamed '{bad}' to '{near}'.",
                    )
            # 3E. UnboundLocalError accumulator initialization
            if contextual and error_type == "UnboundLocalError":
                tr = _InsertInitBeforeLineTransformer(line_no, bad, "0")
                new_code, changed = _run_transformer(code, tr)
                if changed:
                    return (
                        new_code,
                        f"L{line_no} [CST_FIX]: Initialized local accumulator '{bad} = 0' before update",
                        f"Mistake: Local variable '{bad}' was updated before being given an initial value on line {line_no}.\n"
                        "Reason: An augmented assignment (+=, -=) needs a starting value.\n"
                        f"Fix: Initialized '{bad} = 0' right before use.",
                    )

    # 4. TypeError
    elif error_type == "TypeError":
        tr = _TypeErrorCSTTransformer(line_no, emsg, fn_return_type=fn_return_type)
        new_code, changed = _run_transformer(code, tr)
        if changed:
            return (
                new_code,
                f"L{line_no} [CST_FIX]: {tr.action_note or 'Fixed TypeError'}",
                "",
            )

    # 5. IndexError (contextual mode)
    elif error_type == "IndexError" and contextual:
        tr = _IndexErrorCSTTransformer(line_no)
        new_code, changed = _run_transformer(code, tr)
        if changed:
            return (
                new_code,
                f"L{line_no} [CST_FIX]: {tr.action_note}",
                "",
            )

    # 6. KeyError
    elif error_type == "KeyError":
        tr = _KeyErrorCSTTransformer(line_no, allow_direct_get=contextual)
        new_code, changed = _run_transformer(code, tr)
        if changed:
            return (
                new_code,
                f"L{line_no} [CST_FIX]: {tr.action_note}",
                "",
            )

    # 7. AttributeError
    elif error_type == "AttributeError":
        tr = _AttributeErrorCSTTransformer(line_no, emsg)
        new_code, changed = _run_transformer(code, tr)
        if changed:
            return (
                new_code,
                f"L{line_no} [CST_FIX]: {tr.action_note}",
                "",
            )

    # 8. ValueError
    elif error_type == "ValueError":
        tr = _ValueErrorCSTTransformer(line_no, emsg)
        new_code, changed = _run_transformer(code, tr)
        if changed:
            return (
                new_code,
                f"L{line_no} [CST_FIX]: Repaired ValueError conversion",
                "",
            )

    # 9. ModuleNotFoundError
    elif error_type == "ModuleNotFoundError":
        mod_name = _quoted(emsg)
        top = mod_name.split(".")[0] if mod_name else ""
        near = _stdlib_near(top) if top else None
        if near:
            tr = _ModuleNotFoundCSTTransformer(line_no, top, near)
            new_code, changed = _run_transformer(code, tr)
            if changed:
                return (
                    new_code,
                    f"L{line_no} [CST_FIX]: Fixed stdlib import typo '{top}' -> '{near}'",
                    "",
                )

    return code, "", ""


# ---------------------------------------------------------------------------
# Security Hardening CST Transformer
# ---------------------------------------------------------------------------

class _SecurityHardeningCSTTransformer(cst.CSTTransformer):
    """
    Applies targeted security hardening mutations directly on the Python CST,
    preserving comments, multi-line call arguments, and mixed whitespace.
    """
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, findings_by_line: Dict[int, List[Dict[str, Any]]]) -> None:
        self.findings_by_line = findings_by_line
        self.actions: List[str] = []
        self.handled_lines: Set[int] = set()
        self.introduced_imports: Set[str] = set()

    def _findings_for(self, original_node: cst.CSTNode) -> Tuple[Optional[int], Set[str], List[Dict[str, Any]]]:
        pos = self.get_metadata(PositionProvider, original_node, None)
        if pos is None:
            return None, set(), []
        matched: List[Dict[str, Any]] = []
        first_ln: Optional[int] = None
        for ln in range(pos.start.line, pos.end.line + 1):
            if ln in self.findings_by_line:
                if first_ln is None:
                    first_ln = ln
                matched.extend(self.findings_by_line[ln])
        return first_ln, {f["metric_id"] for f in matched}, matched

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.BaseExpression:
        ln, mids, _ = self._findings_for(original_node)
        if not mids or ln is None:
            return updated_node

        # SEC_02: eval(...) -> ast.literal_eval(...)
        if "SEC_02" in mids and isinstance(updated_node.func, cst.Name) and updated_node.func.value == "eval":
            self.handled_lines.add(ln)
            self.introduced_imports.add("ast")
            self.actions.append(f"L{ln} [SEC_02]: Replaced eval() with safe ast.literal_eval()")
            return updated_node.with_changes(
                func=cst.Attribute(value=cst.Name("ast"), attr=cst.Name("literal_eval"))
            )

        # SEC_03: yaml.load / yaml.unsafe_load -> yaml.safe_load; pickle/marshal.load(s) -> json.loads
        if "SEC_03" in mids and isinstance(updated_node.func, cst.Attribute):
            obj, attr = updated_node.func.value, updated_node.func.attr.value
            if isinstance(obj, cst.Name) and obj.value == "yaml" and attr in ("load", "unsafe_load"):
                self.handled_lines.add(ln)
                self.actions.append(f"L{ln} [SEC_03]: Replaced yaml.{attr} with yaml.safe_load()")
                return updated_node.with_changes(
                    func=updated_node.func.with_changes(attr=cst.Name("safe_load"))
                )
            if isinstance(obj, cst.Name) and obj.value in ("pickle", "cPickle", "marshal", "dill") and attr in ("load", "loads"):
                self.handled_lines.add(ln)
                self.introduced_imports.add("json")
                self.actions.append(f"L{ln} [SEC_03]: Replaced unsafe {obj.value}.{attr} with json.loads()")
                return updated_node.with_changes(
                    func=cst.Attribute(value=cst.Name("json"), attr=cst.Name("loads"))
                )

        # SEC_17: tempfile.mktemp() -> tempfile.mkstemp()
        if "SEC_17" in mids and isinstance(updated_node.func, cst.Attribute) and updated_node.func.attr.value == "mktemp":
            self.handled_lines.add(ln)
            self.actions.append(f"L{ln} [SEC_17]: Replaced tempfile.mktemp() with tempfile.mkstemp()")
            return updated_node.with_changes(
                func=updated_node.func.with_changes(attr=cst.Name("mkstemp"))
            )

        # SEC_19: os.chmod(path, 0o777) -> 0o600
        if "SEC_19" in mids and isinstance(updated_node.func, cst.Attribute) and updated_node.func.attr.value == "chmod":
            new_args = []
            changed = False
            for arg in updated_node.args:
                if isinstance(arg.value, cst.Integer) and arg.value.value in ("0o777", "0777", "0o666", "0666", "0o775", "0775"):
                    new_args.append(arg.with_changes(value=cst.Integer("0o600")))
                    changed = True
                else:
                    new_args.append(arg)
            if changed:
                self.handled_lines.add(ln)
                self.actions.append(f"L{ln} [SEC_19]: Hardened os.chmod permission to 0o600")
                return updated_node.with_changes(args=new_args)

        # SEC_23: hashlib.md5/sha1 -> hashlib.sha256; hashlib.new('md5') -> hashlib.new('sha256')
        if "SEC_23" in mids and isinstance(updated_node.func, cst.Attribute):
            obj, attr = updated_node.func.value, updated_node.func.attr.value
            if isinstance(obj, cst.Name) and obj.value == "hashlib" and attr in ("md5", "sha1"):
                self.handled_lines.add(ln)
                self.actions.append(f"L{ln} [SEC_23]: Upgraded deprecated MD5/SHA1 hash to SHA-256")
                return updated_node.with_changes(
                    func=updated_node.func.with_changes(attr=cst.Name("sha256"))
                )
            if isinstance(obj, cst.Name) and obj.value == "hashlib" and attr == "new" and updated_node.args:
                a0 = updated_node.args[0]
                if isinstance(a0.value, cst.SimpleString):
                    try:
                        alg = ast.literal_eval(a0.value.value)
                    except Exception:
                        alg = ""
                    if isinstance(alg, str) and alg.lower() in ("md5", "sha1"):
                        self.handled_lines.add(ln)
                        self.actions.append(f"L{ln} [SEC_23]: Upgraded deprecated MD5/SHA1 hash to SHA-256")
                        new_args = [a0.with_changes(value=cst.SimpleString("'sha256'"))] + list(updated_node.args[1:])
                        return updated_node.with_changes(args=new_args)

        # SEC_26: verify=False -> verify=True
        if "SEC_26" in mids:
            new_args = []
            changed = False
            for arg in updated_node.args:
                if (
                    arg.keyword is not None
                    and arg.keyword.value == "verify"
                    and isinstance(arg.value, cst.Name)
                    and arg.value.value == "False"
                ):
                    new_args.append(arg.with_changes(value=cst.Name("True")))
                    changed = True
                else:
                    new_args.append(arg)
            if changed:
                self.handled_lines.add(ln)
                self.actions.append(f"L{ln} [SEC_26]: Enforced TLS certificate verification (verify=True)")
                updated_node = updated_node.with_changes(args=new_args)

        # SEC_27: Weak RSA key size (512|1024 -> 2048)
        if "SEC_27" in mids:
            fn_name = (
                updated_node.func.attr.value
                if isinstance(updated_node.func, cst.Attribute)
                else (updated_node.func.value if isinstance(updated_node.func, cst.Name) else "")
            )
            if fn_name in ("generate", "generate_private_key"):
                new_args = []
                changed = False
                for arg in updated_node.args:
                    if isinstance(arg.value, cst.Integer) and arg.value.value in ("512", "1024"):
                        new_args.append(arg.with_changes(value=cst.Integer("2048")))
                        changed = True
                    else:
                        new_args.append(arg)
                if changed:
                    self.handled_lines.add(ln)
                    self.actions.append(f"L{ln} [SEC_27]: Upgraded cryptographic key size to 2048 bits")
                    return updated_node.with_changes(args=new_args)

        # SEC_33: debug=True -> debug=False
        if "SEC_33" in mids:
            new_args = []
            changed = False
            for arg in updated_node.args:
                if (
                    arg.keyword is not None
                    and arg.keyword.value == "debug"
                    and isinstance(arg.value, cst.Name)
                    and arg.value.value == "True"
                ):
                    new_args.append(arg.with_changes(value=cst.Name("False")))
                    changed = True
                else:
                    new_args.append(arg)
            if changed:
                self.handled_lines.add(ln)
                self.actions.append(f"L{ln} [SEC_33]: Disabled production debug mode (debug=False)")
                updated_node = updated_node.with_changes(args=new_args)

        # SEC_35: .read() -> .read(65536)
        if (
            "SEC_35" in mids
            and isinstance(updated_node.func, cst.Attribute)
            and updated_node.func.attr.value == "read"
            and len(updated_node.args) == 0
        ):
            self.handled_lines.add(ln)
            self.actions.append(f"L{ln} [SEC_35]: Bounded unbounded .read() to 65536 bytes")
            return updated_node.with_changes(args=[cst.Arg(value=cst.Integer("65536"))])

        # SEC_39: requests.<fn>(...) missing timeout -> add timeout=10
        if (
            "SEC_39" in mids
            and isinstance(updated_node.func, cst.Attribute)
            and isinstance(updated_node.func.value, cst.Name)
            and updated_node.func.value.value == "requests"
            and not any(a.keyword and a.keyword.value == "timeout" for a in updated_node.args)
        ):
            self.handled_lines.add(ln)
            self.actions.append(f"L{ln} [SEC_39]: Added timeout=10 to network request")
            args = list(updated_node.args)
            if args and args[-1].comma == cst.MaybeSentinel.DEFAULT:
                args[-1] = args[-1].with_changes(
                    comma=cst.Comma(whitespace_after=cst.SimpleWhitespace(" "))
                )
            args.append(
                cst.Arg(
                    keyword=cst.Name("timeout"),
                    equal=cst.AssignEqual(
                        whitespace_before=cst.SimpleWhitespace(""),
                        whitespace_after=cst.SimpleWhitespace(""),
                    ),
                    value=cst.Integer("10"),
                )
            )
            return updated_node.with_changes(args=args)

        # SEC_04: cursor.execute(f"...{var}...") -> parameterized query on CST
        if (
            "SEC_04" in mids
            and isinstance(updated_node.func, cst.Attribute)
            and updated_node.func.attr.value == "execute"
            and len(updated_node.args) == 1
            and isinstance(updated_node.args[0].value, cst.FormattedString)
        ):
            fstr = updated_node.args[0].value
            sql_parts: List[str] = []
            params: List[cst.Element] = []
            for part in fstr.parts:
                if isinstance(part, cst.FormattedStringText):
                    sql_parts.append(part.value)
                elif isinstance(part, cst.FormattedStringExpression):
                    sql_parts.append("%s")
                    params.append(cst.Element(value=part.expression))
            if params:
                sql_clean = "".join(sql_parts).replace("'%s'", "%s")
                self.handled_lines.add(ln)
                self.actions.append(f"L{ln} [SEC_04]: Parameterized dynamic SQL query with placeholder '%s'")
                if len(params) == 1:
                    params[0] = params[0].with_changes(comma=cst.Comma())
                param_tuple = cst.Tuple(elements=params, lpar=[cst.LeftParen()], rpar=[cst.RightParen()])
                return updated_node.with_changes(
                    args=[
                        cst.Arg(
                            value=cst.SimpleString(f'"{sql_clean}"'),
                            comma=cst.Comma(whitespace_after=cst.SimpleWhitespace(" ")),
                        ),
                        cst.Arg(value=param_tuple),
                    ]
                )

        return updated_node

    def leave_SimpleString(
        self, original_node: cst.SimpleString, updated_node: cst.SimpleString
    ) -> cst.SimpleString:
        ln, mids, _ = self._findings_for(original_node)
        if ln is not None and "SEC_29" in mids and "0.0.0.0" in updated_node.value:
            self.handled_lines.add(ln)
            self.actions.append(f"L{ln} [SEC_29]: Restricted socket bind from 0.0.0.0 to 127.0.0.1")
            return updated_node.with_changes(value=updated_node.value.replace("0.0.0.0", "127.0.0.1"))
        return updated_node

    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.Assign:
        ln, mids, _ = self._findings_for(original_node)
        if ln is not None and "SEC_21" in mids and len(updated_node.targets) == 1:
            tgt = updated_node.targets[0].target
            if isinstance(tgt, cst.Name) and isinstance(updated_node.value, cst.SimpleString):
                env_key = tgt.value.upper()
                self.handled_lines.add(ln)
                self.introduced_imports.add("os")
                self.actions.append(
                    f"L{ln} [SEC_21]: Replaced hardcoded secret '{tgt.value}' with os.environ.get('{env_key}')"
                )
                return updated_node.with_changes(
                    value=cst.parse_expression(f'os.environ.get("{env_key}", "")')
                )
        return updated_node

    def leave_ExceptHandler(
        self, original_node: cst.ExceptHandler, updated_node: cst.ExceptHandler
    ) -> cst.ExceptHandler:
        ln, mids, _ = self._findings_for(original_node)
        if ln is not None and "SEC_45" in mids and updated_node.type is None:
            self.handled_lines.add(ln)
            self.actions.append(f"L{ln} [SEC_45]: Narrowed bare except: to except Exception:")
            return updated_node.with_changes(
                type=cst.Name("Exception"),
                whitespace_after_except=cst.SimpleWhitespace(" "),
            )
        return updated_node

    def leave_SimpleStatementLine(
        self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine:
        ln, mids, matched = self._findings_for(original_node)
        if not mids or ln is None:
            return updated_node
        # Check if any line in this statement was already handled by a fine-grained CST transform
        pos = self.get_metadata(PositionProvider, original_node, None)
        stmt_lines = set(range(pos.start.line, pos.end.line + 1)) if pos else {ln}
        if stmt_lines & self.handled_lines:
            # If any blocking findings remain unhandled on this statement, still check below
            remaining_blocking = [
                f for f in matched
                if f.get("severity") in ("CRITICAL", "HIGH") and f.get("line") not in self.handled_lines
            ]
            if not remaining_blocking:
                return updated_node

        def _make_sanitized(stmt_code: str, comment_text: str) -> cst.SimpleStatementLine:
            parsed = cst.parse_statement(stmt_code + "\n")
            assert isinstance(parsed, cst.SimpleStatementLine)
            return parsed.with_changes(
                leading_lines=original_node.leading_lines,
                trailing_whitespace=cst.TrailingWhitespace(
                    whitespace=cst.SimpleWhitespace("  "),
                    comment=cst.Comment(f"# {comment_text}"),
                    newline=original_node.trailing_whitespace.newline,
                ),
            )

        if "SEC_01" in mids:
            self.handled_lines.update(stmt_lines)
            self.actions.append(f"L{ln} [SEC_01]: Neutralized OS command execution sink")
            return _make_sanitized("pass", "[SANITIZED SEC_01] Blocked OS command execution sink")

        if "SEC_02" in mids and ln not in self.handled_lines:
            self.handled_lines.update(stmt_lines)
            self.actions.append(f"L{ln} [SEC_02]: Blocked dynamic exec()/compile()")
            return _make_sanitized("pass", "[SANITIZED SEC_02] Blocked dynamic exec/compile")

        if "SEC_04" in mids and ln not in self.handled_lines:
            self.handled_lines.update(stmt_lines)
            self.actions.append(f"L{ln} [SEC_04]: Neutralized unparameterized SQL sink")
            return _make_sanitized("pass", "[SANITIZED SEC_04] Neutralized unparameterized SQL sink")

        if "SEC_05" in mids:
            self.handled_lines.update(stmt_lines)
            self.actions.append(f"L{ln} [SEC_05]: Neutralized unsafe XML parser")
            raw = cst.Module([]).code_for_node(original_node)
            if "ET.fromstring(" in raw:
                return _make_sanitized("root = None", "[SANITIZED SEC_05] Blocked unsafe XML parser")
            return _make_sanitized("pass", "[SANITIZED SEC_05] Blocked unsafe XML module import")

        if "SEC_06" in mids and "render_template_string(" in cst.Module([]).code_for_node(original_node):
            self.handled_lines.update(stmt_lines)
            self.actions.append(f"L{ln} [SEC_06]: Sanitized dynamic SSTI template string")
            return _make_sanitized("return str(user_bio)", "[AGENTIC_COMPILER SEC_06] Escaped SSTI banner")

        if "SEC_08" in mids:
            self.handled_lines.update(stmt_lines)
            self.actions.append(f"L{ln} [SEC_08]: Blocked dynamic module import")
            return _make_sanitized("pass", "[AGENTIC_COMPILER SEC_08] Blocked dynamic import")

        if mids & {"SEC_09", "SEC_10", "SEC_14"}:
            self.handled_lines.update(stmt_lines)
            tags = ",".join(sorted(mids & {"SEC_09", "SEC_10", "SEC_14"}))
            self.actions.append(f"L{ln} [{tags}]: Neutralized sandbox escape")
            return _make_sanitized("pass", "[AGENTIC_COMPILER] Blocked sandbox escape / reflection vector")

        if "SEC_16" in mids:
            self.handled_lines.update(stmt_lines)
            self.actions.append(f"L{ln} [SEC_16]: Neutralized destructive file operation")
            return _make_sanitized("pass", "[AGENTIC_COMPILER SEC_16] Blocked destructive file deletion")

        # Universal safety net for any remaining CRITICAL/HIGH finding on this statement
        blocking = [f for f in matched if f.get("severity") in ("CRITICAL", "HIGH")]
        if blocking and updated_node == original_node:
            blocking_mids = ",".join(sorted({f["metric_id"] for f in blocking}))
            self.handled_lines.update(stmt_lines)
            self.actions.append(f"L{ln} [{blocking_mids}]: Neutralized blocking security threat")
            first_small = original_node.body[0] if original_node.body else None
            if isinstance(first_small, cst.Return):
                return _make_sanitized("return None", f"[SANITIZED {blocking_mids}] Neutralized unsafe return")
            if isinstance(first_small, cst.Assign) and first_small.targets and isinstance(first_small.targets[0].target, cst.Name):
                var_n = first_small.targets[0].target.value
                return _make_sanitized(f"{var_n} = None", f"[SANITIZED {blocking_mids}] Neutralized unsafe assignment")
            return _make_sanitized("pass", f"[SANITIZED {blocking_mids}] Neutralized blocking security threat")

        return updated_node


def harden_python_security_cst(
    code: str, audit_report: Dict[str, Any]
) -> Optional[Tuple[str, List[str]]]:
    """
    Harden Python security vulnerabilities directly on the LibCST tree.
    For large files (>120 lines), uses C-speed `ast.parse` to run LibCST only on the
    top-level statements containing security findings, keeping untouched statements byte-identical.
    Returns `(hardened_code, actions)` or `None` if `code` cannot be parsed into a CST.
    """
    lines_with_ends = code.splitlines(keepends=True)
    total_lines = len(lines_with_ends)
    findings_by_line: Dict[int, List[Dict[str, Any]]] = {}
    for f in audit_report.get("findings", []):
        ln = f.get("line", 1)
        if isinstance(ln, int) and 1 <= ln <= total_lines:
            findings_by_line.setdefault(ln, []).append(f)
    if not findings_by_line:
        try:
            ast.parse(code)
            return code, []
        except Exception:
            return None

    # Fast sliced path for large files: only parse/transform top-level statements that have findings.
    if total_lines > _SLICE_LINE_THRESHOLD:
        try:
            tree = ast.parse(code)
        except Exception:
            return None
        affected_spans: List[Tuple[int, int, Dict[int, List[Dict[str, Any]]]]] = []
        covered_lines: Set[int] = set()
        for stmt in tree.body:
            s_start, s_end = _stmt_line_span(stmt)
            local_findings: Dict[int, List[Dict[str, Any]]] = {}
            for ln in range(s_start, s_end + 1):
                if ln in findings_by_line:
                    local_findings[ln - s_start + 1] = findings_by_line[ln]
                    covered_lines.add(ln)
            if local_findings:
                affected_spans.append((s_start, s_end, local_findings))

        if affected_spans and covered_lines == set(findings_by_line.keys()):
            out_chunks: List[str] = []
            all_actions: List[str] = []
            all_imports: Set[str] = set()
            cursor = 0  # 0-based index into lines_with_ends
            slice_ok = True
            for s_start, s_end, local_findings in affected_spans:
                out_chunks.extend(lines_with_ends[cursor : s_start - 1])
                slice_code = "".join(lines_with_ends[s_start - 1 : s_end])
                mod = parse_cst(slice_code)
                if mod is None:
                    slice_ok = False
                    break
                tr = _SecurityHardeningCSTTransformer(local_findings)
                try:
                    wrapper = MetadataWrapper(mod)
                    new_mod = wrapper.visit(tr)
                    out_chunks.append(new_mod.code)
                except Exception:
                    slice_ok = False
                    break
                offset = s_start - 1
                for act in tr.actions:
                    all_actions.append(
                        re.sub(r"^L(\d+)\b", lambda m, off=offset: f"L{int(m.group(1)) + off}", act)
                    )
                all_imports.update(tr.introduced_imports)
                cursor = s_end
            if slice_ok:
                out_chunks.extend(lines_with_ends[cursor:])
                hardened = "".join(out_chunks)
                if all_imports:
                    hardened = ensure_imports_cst(hardened, sorted(all_imports))
                return hardened, all_actions

    mod = parse_cst(code)
    if mod is None:
        return None
    tr = _SecurityHardeningCSTTransformer(findings_by_line)
    try:
        wrapper = MetadataWrapper(mod)
        new_mod = wrapper.visit(tr)
        hardened = new_mod.code
    except Exception:
        return None

    if tr.introduced_imports:
        hardened = ensure_imports_cst(hardened, sorted(tr.introduced_imports))
    return hardened, tr.actions


# ---------------------------------------------------------------------------
# Single-Issue CST Patch Application (Replaces applySingleIssuePatch slicing)
# ---------------------------------------------------------------------------

class _StatementPatchCSTTransformer(cst.CSTTransformer):
    """
    Applies a statement-level replacement or insertion directly on the CST at `target_line`.
    Preserves:
      - leading comments / blank lines on the replaced statement
      - trailing inline comments on the replaced statement (when not already in replacement)
      - multi-line original statements (replaces the entire CST statement node, no orphan lines!)
      - exact parent IndentedBlock indentation (tabs, 2 spaces, 4 spaces, mixed)
    """
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(
        self,
        target_line: int,
        replacement_stmts: Sequence[cst.BaseStatement],
        insert_only: bool = False,
    ) -> None:
        self.target_line = target_line
        self.replacement_stmts = list(replacement_stmts)
        self.insert_only = insert_only
        self.changed = False

    def _patch_stmt_list(
        self, orig_body: Sequence[cst.BaseStatement], upd_body: Sequence[cst.BaseStatement]
    ) -> Tuple[List[cst.BaseStatement], bool]:
        if self.changed:
            return list(upd_body), False
        for i, orig_stmt in enumerate(orig_body):
            pos = self.get_metadata(PositionProvider, orig_stmt, None)
            if pos is None or not _covers_line(pos, self.target_line):
                continue

            # If orig_stmt is a compound statement (if/for/while/def/class/with/try) and
            # target_line is strictly inside its body (not on the header line), let
            # leave_IndentedBlock handle the inner statement instead!
            if isinstance(orig_stmt, cst.BaseCompoundStatement) and pos.start.line < self.target_line:
                continue

            new_body = list(upd_body)
            if self.insert_only:
                new_body[i:i] = self.replacement_stmts
                self.changed = True
                return new_body, True

            # Replacement of a SimpleStatementLine (single or multi-line!)
            if isinstance(orig_stmt, cst.SimpleStatementLine):
                repl = list(self.replacement_stmts)
                if repl and hasattr(repl[0], "leading_lines"):
                    repl[0] = repl[0].with_changes(leading_lines=orig_stmt.leading_lines)
                # Preserve trailing inline comment if the replacement doesn't include one
                if (
                    repl
                    and isinstance(repl[-1], cst.SimpleStatementLine)
                    and orig_stmt.trailing_whitespace.comment is not None
                    and repl[-1].trailing_whitespace.comment is None
                ):
                    repl[-1] = repl[-1].with_changes(
                        trailing_whitespace=orig_stmt.trailing_whitespace
                    )
                new_body[i : i + 1] = repl
                self.changed = True
                return new_body, True

        return list(upd_body), False

    def leave_IndentedBlock(
        self, original_node: cst.IndentedBlock, updated_node: cst.IndentedBlock
    ) -> cst.IndentedBlock:
        new_body, patched = self._patch_stmt_list(original_node.body, updated_node.body)
        return updated_node.with_changes(body=new_body) if patched else updated_node

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.Module:
        new_body, patched = self._patch_stmt_list(original_node.body, updated_node.body)
        return updated_node.with_changes(body=new_body) if patched else updated_node


def _parse_replacement_statements(plus_lines: Sequence[str]) -> Optional[List[cst.BaseStatement]]:
    """Parse one or more `+` patch lines into LibCST statement nodes."""
    text = "\n".join(plus_lines).strip()
    if not text:
        return None
    try:
        mod = cst.parse_module(text + "\n")
        if mod.body:
            return list(mod.body)
    except cst.ParserSyntaxError:
        pass
    return None


def _compute_patched_lines(before: str, after: str, fallback_line: int) -> List[int]:
    """Return 1-based line numbers in `after` that were added or modified."""
    a, b = before.split("\n"), after.split("\n")
    patched: List[int] = []
    for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag in ("replace", "insert"):
            patched.extend(range(j1 + 1, j2 + 1))
    return patched or [fallback_line]


def apply_single_issue_patch_cst(
    code: str,
    issue: Dict[str, Any],
    language: str = "python",
) -> Dict[str, Any]:
    """
    Apply a single diagnostic issue patch using LibCST (for Python) instead of
    frontend string slicing and indentation guessing.

    Returns a dict:
      {
        "code": <patched source>,
        "changed": <bool>,
        "engine": "libcst" | "libcst_statement" | "syntax_rule" | "cpp_fallback",
        "target_line": <int>,
        "line_delta": <int>,
        "patched_lines": [<int>, ...],
      }
    """
    target_line = int(issue.get("line") or 1)
    patch_entries = issue.get("patch") or []
    plus_lines = [p.get("text", "") for p in patch_entries if p.get("sign") == "+"]
    has_minus = any(p.get("sign") == "-" for p in patch_entries)

    if language != "python":
        # Non-Python (C++) clean fallback
        lines = code.split("\n")
        if not plus_lines:
            return {
                "code": code, "changed": False, "engine": "cpp_fallback",
                "target_line": target_line, "line_delta": 0, "patched_lines": [],
            }
        if has_minus:
            idx = target_line - 1
            if 0 <= idx < len(lines):
                indent = re.match(r"^(\s*)", lines[idx]).group(1)
                rep = [indent + t.strip() for t in plus_lines]
                lines[idx : idx + 1] = rep
        else:
            p_text = plus_lines[0].strip()
            ins_idx = 0 if p_text.startswith("#include") else max(0, target_line - 1)
            ref_indent = re.match(r"^(\s*)", lines[ins_idx]).group(1) if 0 < ins_idx < len(lines) else ""
            lines.insert(ins_idx, ref_indent + p_text)
            target_line = ins_idx + 1
        new_code = "\n".join(lines)
        return {
            "code": new_code,
            "changed": new_code != code,
            "engine": "cpp_fallback",
            "target_line": target_line,
            "line_delta": new_code.count("\n") - code.count("\n"),
            "patched_lines": _compute_patched_lines(code, new_code, target_line),
        }

    # --- Python Strategy 1: Direct Semantic CST Mutation ---
    etype = issue.get("type") or ""
    emsg = issue.get("error_message") or issue.get("mistake") or issue.get("reason") or ""
    suggestion = issue.get("suggestion")
    err_var = issue.get("error_variable")

    # Parse once with C-speed ast.parse to check syntax validity AND gather scope symbols
    ast_tree: Optional[ast.Module] = None
    try:
        ast_tree = ast.parse(code)
    except Exception:
        ast_tree = None

    if ast_tree is not None and etype:
        enclosing_class = None
        class_attrs: Set[str] = set()
        local_syms: Set[str] = set()
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.ClassDef):
                if getattr(node, "lineno", 0) <= target_line <= getattr(node, "end_lineno", 0):
                    enclosing_class = node.name
                    for cn in ast.walk(node):
                        if isinstance(cn, ast.Attribute) and isinstance(cn.value, ast.Name) and cn.value.id == "self":
                            class_attrs.add(cn.attr)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if getattr(node, "lineno", 0) <= target_line <= getattr(node, "end_lineno", 0):
                    for fn in ast.walk(node):
                        if isinstance(fn, ast.Name):
                            local_syms.add(fn.id)

        new_code, _act, _expl = apply_functional_cst_fix(
            code,
            error_type=etype,
            error_message=emsg,
            line_no=target_line,
            suggestion=suggestion,
            error_variable=err_var,
            enclosing_class=enclosing_class,
            class_attributes=class_attrs,
            local_symbols=local_syms,
            contextual=True,
        )
        if new_code != code:
            patched_lines = _compute_patched_lines(code, new_code, target_line)
            return {
                "code": new_code,
                "changed": True,
                "engine": "libcst",
                "target_line": patched_lines[0],
                "line_delta": new_code.count("\n") - code.count("\n"),
                "patched_lines": patched_lines,
            }

    # --- Python Strategy 2: CST Statement-Level Replacement / Insertion ---
    if plus_lines and ast_tree is not None:
        # Import insertion shortcut: insert directly into CST Module.body
        if not has_minus and len(plus_lines) == 1 and re.match(r"^(?:import\s+|from\s+)", plus_lines[0].strip()):
            m_simple = re.fullmatch(r"import\s+([A-Za-z_]\w*)", plus_lines[0].strip())
            if m_simple:
                new_code = ensure_imports_cst(code, [m_simple.group(1)])
            else:
                imp_stmt = _parse_replacement_statements(plus_lines)
                new_code = code
                if imp_stmt:
                    mod = parse_cst(code)
                    if mod is not None:
                        idx = _import_insert_index(mod)
                        body = list(mod.body)
                        if idx == 0 and body and hasattr(body[0], "leading_lines") and body[0].leading_lines:
                            imp_stmt[0] = imp_stmt[0].with_changes(leading_lines=body[0].leading_lines)
                            body[0] = body[0].with_changes(leading_lines=())
                        new_code = mod.with_changes(body=body[:idx] + imp_stmt + body[idx:]).code
            if new_code != code:
                patched_lines = _compute_patched_lines(code, new_code, 1)
                return {
                    "code": new_code,
                    "changed": True,
                    "engine": "libcst_statement",
                    "target_line": patched_lines[0],
                    "line_delta": new_code.count("\n") - code.count("\n"),
                    "patched_lines": patched_lines,
                }

        repl_stmts = _parse_replacement_statements(plus_lines)
        if repl_stmts:
            tr = _StatementPatchCSTTransformer(
                target_line=target_line,
                replacement_stmts=repl_stmts,
                insert_only=not has_minus,
            )
            new_code, changed = _run_transformer(code, tr)
            if changed:
                patched_lines = _compute_patched_lines(code, new_code, target_line)
                return {
                    "code": new_code,
                    "changed": True,
                    "engine": "libcst_statement",
                    "target_line": patched_lines[0],
                    "line_delta": new_code.count("\n") - code.count("\n"),
                    "patched_lines": patched_lines,
                }

    # --- Python Strategy 3: SyntaxError / Unparseable Code Rule Repair ---
    if ast_tree is None:
        from nlp_explainer import NLPExplainer
        ir = {
            "error_type": etype or "SyntaxError",
            "error_message": emsg,
            "line_number": target_line,
            "suggestion": suggestion,
        }
        new_code = NLPExplainer().generate_fixed_code(ir, code)
        if new_code != code:
            patched_lines = _compute_patched_lines(code, new_code, target_line)
            return {
                "code": new_code,
                "changed": True,
                "engine": "syntax_rule",
                "target_line": patched_lines[0],
                "line_delta": new_code.count("\n") - code.count("\n"),
                "patched_lines": patched_lines,
            }

    return {
        "code": code,
        "changed": False,
        "engine": "libcst",
        "target_line": target_line,
        "line_delta": 0,
        "patched_lines": [],
    }
