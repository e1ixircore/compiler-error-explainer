# ir_generator.py
import ast
from functools import lru_cache
import json


@lru_cache(maxsize=16)
def cached_ast_parse(code):
    """Cached ast.parse(code) returning an ast.Module or None on syntax error.
    Do NOT mutate returned AST nodes (e.g. do not attach .parent attributes)."""
    try:
        return ast.parse(code)
    except Exception:
        return None


def _find_enclosing_top_stmt(tree, line_number):
    if tree is None or not line_number:
        return None
    for stmt in tree.body:
        start = getattr(stmt, "lineno", 0)
        decs = getattr(stmt, "decorator_list", None)
        if decs:
            start = min(start, *(getattr(d, "lineno", start) for d in decs))
        end = getattr(stmt, "end_lineno", None) or start
        if start <= line_number <= end:
            return stmt
    return None


class IRGenerator:

    def __init__(self, code, error_obj):
        self.code = code
        self.error = error_obj
        self._tree = cached_ast_parse(code)

    def get_ast_info(self):
        tree = self._tree
        if tree is None:
            return None, None
        target_ln = self.error.line_number
        top_stmt = _find_enclosing_top_stmt(tree, target_ln)
        root = top_stmt if top_stmt is not None else tree
        root_parent = tree if top_stmt is not None else None

        # BFS over ONLY the enclosing top-level statement (orders of magnitude faster on 2,000+ LOC files)
        stack = [(root, root_parent)]
        while stack:
            node, parent = stack.pop(0)
            if getattr(node, "lineno", None) == target_ln:
                node_name = type(node).__name__
                parent_name = type(parent).__name__ if parent is not None else None
                return node_name, parent_name
            for child in ast.iter_child_nodes(node):
                stack.append((child, node))
        return None, None

    def get_variables(self):
        tree = self._tree
        if tree is None:
            return []
        top_stmt = _find_enclosing_top_stmt(tree, self.error.line_number)
        root = top_stmt if (top_stmt is not None and len(tree.body) > 20) else tree
        return list({node.id for node in ast.walk(root) if isinstance(node, ast.Name)})

    def extract_error_variable(self):
        msg = self.error.message

        # NameError
        if "name '" in msg:
            return msg.split("'")[1]

        # KeyError
        if "KeyError" in self.error.error_type or "'" in msg:
            return msg.replace("'", "")

        return None

    def get_indentation_level(self):
        try:
            lines = self.code.split("\n")
            line = lines[self.error.line_number - 1]
            return len(line) - len(line.lstrip())
        except:
            return None

    def generate_ir(self):

        ast_node, parent_node = self.get_ast_info()

        ir = {
            "error_type": self.error.error_type,
            "error_message": self.error.message,
            "error_category": self.error.category,
            "line_number": self.error.line_number,
            "ast_node": ast_node,
            "parent_node": parent_node,
            "variables_used": self.get_variables(),
            "error_variable": self.extract_error_variable(),
            "indentation_level": self.get_indentation_level(),
            "traceback": self.error.traceback_info
        }

        return json.dumps(ir, indent=4)