# ir_generator.py
import ast
import json

class IRGenerator:

    def __init__(self, code, error_obj):
        self.code = code
        self.error = error_obj

    def attach_parents(self, tree):
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                child.parent = parent

    def get_ast_info(self):
        try:
            tree = ast.parse(self.code)
            self.attach_parents(tree)

            for node in ast.walk(tree):
                if hasattr(node, "lineno") and node.lineno == self.error.line_number:
                    node_name = type(node).__name__
                    parent_name = type(node.parent).__name__ if hasattr(node, "parent") else None
                    return node_name, parent_name
        except:
            pass

        return None, None

    def get_variables(self):
        variables = set()

        try:
            tree = ast.parse(self.code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    variables.add(node.id)

        except:
            pass

        return list(variables)

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