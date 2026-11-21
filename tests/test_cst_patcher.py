"""
tests/test_cst_patcher.py
=========================
Comprehensive tests for LibCST-based Concrete Syntax Tree (CST) code mutation
and single-issue patch application, specifically validating cases where string
slicing and indentation guessing break:
  - multi-line expressions and parenthesized continuations
  - inline, leading, and trailing comments (plus '#' inside strings)
  - mixed whitespace and tab / 2-space indentation
  - CST-level security hardening on multi-line calls/statements
  - Flask POST /api/apply-patch endpoint integration
"""

import ast
import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import app as flask_app
from cst_patcher import (
    apply_functional_cst_fix,
    apply_single_issue_patch_cst,
    ensure_imports_cst,
    harden_python_security_cst,
)
from security_metrics_engine import SecurityMetricsEngine


class TestCSTMultiLineAndCommentPreservation(unittest.TestCase):
    """Verify CST mutations preserve comments, multi-line layout, and exact whitespace."""

    def test_multiline_type_error_concat_preserves_comments_and_layout(self) -> None:
        code = (
            "def build_msg(count):\n"
            "    # leading comment\n"
            "    msg = (\n"
            '        "Items: "  # prefix comment\n'
            "        + count    # count comment\n"
            "    )  # closing comment\n"
            "    return msg\n"
        )
        fixed, _, _ = apply_functional_cst_fix(
            code,
            error_type="TypeError",
            error_message='can only concatenate str (not "int") to str',
            line_no=5,
        )
        self.assertIn("+ str(count)", fixed)
        self.assertIn("# leading comment", fixed)
        self.assertIn("# prefix comment", fixed)
        self.assertIn("# count comment", fixed)
        self.assertIn("# closing comment", fixed)
        ast.parse(fixed)

    def test_multiline_logical_is_to_eq_preserves_comments(self) -> None:
        code = (
            "def check(mode):\n"
            "    if (\n"
            "        mode  # current mode\n"
            '        is "active"  # compare literal\n'
            "    ):\n"
            "        return True\n"
            "    return False\n"
        )
        fixed, _, _ = apply_functional_cst_fix(
            code,
            error_type="LogicalError",
            error_message="using identity operator 'is' with a literal",
            line_no=4,
        )
        self.assertIn('== "active"', fixed)
        self.assertNotIn('is "active"', fixed)
        self.assertIn("# current mode", fixed)
        self.assertIn("# compare literal", fixed)
        ast.parse(fixed)

    def test_multiline_assert_tuple_unwrap_preserves_trailing_comment(self) -> None:
        code = (
            "def validate(x):\n"
            "    assert (\n"
            "        x > 0,\n"
            '        "must be positive"\n'
            "    )  # keep this comment\n"
        )
        fixed, _, _ = apply_functional_cst_fix(
            code,
            error_type="LogicalError",
            error_message="assert on a non-empty tuple is always True",
            line_no=2,
        )
        self.assertIn("assert x > 0,", fixed)
        self.assertIn("# keep this comment", fixed)
        tree = ast.parse(fixed)
        assert_node = [n for n in ast.walk(tree) if isinstance(n, ast.Assert)][0]
        self.assertIsNotNone(assert_node.msg)

    def test_multiline_zero_division_preserves_comments(self) -> None:
        code = (
            "def ratio(a):\n"
            "    return (\n"
            "        a  # numerator\n"
            "        / 0  # bad zero divisor\n"
            "    )\n"
        )
        fixed, _, _ = apply_functional_cst_fix(
            code,
            error_type="ZeroDivisionError",
            error_message="division by zero",
            line_no=4,
            contextual=True,
        )
        self.assertIn("/ 1  # bad zero divisor", fixed)
        self.assertIn("# numerator", fixed)
        ast.parse(fixed)

    def test_name_error_rename_skips_comments_strings_and_attributes_but_fixes_fstrings(self) -> None:
        code = (
            "def f(obj):\n"
            "    total = 10\n"
            '    # totla in comment should stay totla\n'
            '    msg = f"totla={totla}" + obj.totla  # totla comment\n'
            "    return msg\n"
        )
        fixed, _, _ = apply_functional_cst_fix(
            code,
            error_type="NameError",
            error_message="name 'totla' is not defined",
            line_no=4,
            suggestion="total",
        )
        self.assertIn("# totla in comment should stay totla", fixed)
        self.assertIn('f"totla={total}"', fixed)
        self.assertIn("obj.totla", fixed)
        self.assertIn("# totla comment", fixed)
        ast.parse(fixed)


class TestCSTTabAndMixedWhitespacePreservation(unittest.TestCase):
    """Verify CST mutations preserve tab indentation and 2-space indentation without guessing."""

    def test_tab_indented_unbound_local_inserts_with_exact_tabs(self) -> None:
        code = (
            "def accumulate(items):\n"
            "\tfor x in items:\n"
            "\t\ttotal += x  # accumulate\n"
            "\treturn total\n"
        )
        fixed, _, _ = apply_functional_cst_fix(
            code,
            error_type="UnboundLocalError",
            error_message="local variable 'total' referenced before assignment",
            line_no=3,
            contextual=True,
        )
        self.assertIn("\t\ttotal = 0\n\t\ttotal += x  # accumulate\n", fixed)
        ast.parse(fixed)

    def test_two_space_indented_statement_patch_preserves_indent_and_comments(self) -> None:
        code = (
            "def f():\n"
            "  # comment above\n"
            "  x = (\n"
            "    1 +\n"
            "    2\n"
            "  )  # trailing note\n"
            "  return x\n"
        )
        issue = {
            "line": 3,
            "type": "CustomPatch",
            "patch": [
                {"sign": "-", "text": "x = ("},
                {"sign": "+", "text": "x = 10"},
            ],
        }
        res = apply_single_issue_patch_cst(code, issue, language="python")
        self.assertTrue(res["changed"])
        self.assertEqual(res["engine"], "libcst_statement")
        # Replaced the entire multi-line statement cleanly with 2-space indent, no orphan lines!
        self.assertIn("  # comment above\n  x = 10  # trailing note\n  return x\n", res["code"])
        ast.parse(res["code"])

    def test_ensure_imports_preserves_header_comments_and_docstring(self) -> None:
        code = (
            "# Header comment\n"
            '"""Module docstring."""\n'
            "from __future__ import annotations\n"
            "\n"
            "x = math.sqrt(4)\n"
        )
        fixed = ensure_imports_cst(code, ["math"])
        lines = fixed.splitlines()
        self.assertEqual(lines[0], "# Header comment")
        self.assertEqual(lines[1], '"""Module docstring."""')
        self.assertEqual(lines[2], "from __future__ import annotations")
        self.assertIn("import math", lines[3:5])
        ast.parse(fixed)


class TestCSTSecurityHardening(unittest.TestCase):
    """Verify LibCST security hardening handles multi-line calls and preserves comments."""

    def test_multiline_requests_verify_false_and_missing_timeout(self) -> None:
        code = (
            "import requests\n"
            "resp = requests.get(\n"
            '    "https://example.com",  # endpoint\n'
            "    verify=False,  # insecure\n"
            ")\n"
        )
        engine = SecurityMetricsEngine()
        audit = engine.analyze(code, language="python")
        res = harden_python_security_cst(code, audit)
        self.assertIsNotNone(res)
        hardened, actions = res
        self.assertIn("verify=True", hardened)
        self.assertNotIn("verify=False", hardened)
        self.assertIn("timeout=10", hardened)
        self.assertIn("# endpoint", hardened)
        self.assertIn("# insecure", hardened)
        self.assertTrue(len(actions) >= 1)
        ast.parse(hardened)

    def test_multiline_os_system_neutralized_as_single_cst_statement(self) -> None:
        code = (
            "import os\n"
            "def run(cmd):\n"
            "    # danger\n"
            "    os.system(\n"
            '        "echo " + cmd\n'
            "    )\n"
            "    return True\n"
        )
        engine = SecurityMetricsEngine()
        audit = engine.analyze(code, language="python")
        res = harden_python_security_cst(code, audit)
        self.assertIsNotNone(res)
        hardened, _ = res
        self.assertIn("pass  # [SANITIZED SEC_01]", hardened)
        self.assertIn("# danger", hardened)
        self.assertIn("return True", hardened)
        # Must parse cleanly — line-based replacement would have left orphan continuation lines!
        ast.parse(hardened)


class TestApplyPatchAPIEndpoint(unittest.TestCase):
    """Integration tests for POST /api/apply-patch backed by LibCST."""

    def setUp(self) -> None:
        self.client = flask_app.app.test_client()

    def test_api_apply_patch_uses_libcst_on_multiline_python(self) -> None:
        code = (
            "def greet(n):\n"
            "\t# tab-indented multi-line expression\n"
            "\treturn (\n"
            '\t\t"Hello "  # greeting\n'
            "\t\t+ n       # number\n"
            "\t)\n"
        )
        resp = self.client.post(
            "/api/apply-patch",
            json={
                "code": code,
                "language": "python",
                "issue": {
                    "line": 5,
                    "type": "TypeError",
                    "error_message": 'can only concatenate str (not "int") to str',
                    "patch": [
                        {"sign": "-", "text": "+ n"},
                        {"sign": "+", "text": "+ str(n)"},
                    ],
                },
            },
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["changed"])
        self.assertEqual(data["engine"], "libcst")
        self.assertIn("+ str(n)", data["code"])
        self.assertIn("# greeting", data["code"])
        self.assertIn("# number", data["code"])
        self.assertIn("\t# tab-indented multi-line expression", data["code"])
        ast.parse(data["code"])

    def test_api_apply_patch_syntax_error_fallback(self) -> None:
        code = "if x > 3  # check\n    print(x)\n"
        resp = self.client.post(
            "/api/apply-patch",
            json={
                "code": code,
                "language": "python",
                "issue": {
                    "line": 1,
                    "type": "SyntaxError",
                    "error_message": "expected ':'",
                    "patch": [
                        {"sign": "-", "text": "if x > 3"},
                        {"sign": "+", "text": "if x > 3:"},
                    ],
                },
            },
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["changed"])
        self.assertEqual(data["engine"], "syntax_rule")
        self.assertIn("if x > 3:", data["code"])
        self.assertIn("# check", data["code"])
        ast.parse(data["code"])


if __name__ == "__main__":
    unittest.main()
