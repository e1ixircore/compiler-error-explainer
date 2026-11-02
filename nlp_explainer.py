"""
nlp_explainer.py - rule-based replacement for the missing explainer.

Contract (what app.py rely on):
    explain(ir: dict) -> str              # must contain "Mistake", "Reason", "Fix"
    generate_fixed_code(ir, code) -> str  # patched source, or original if unsafe

Design: NO LLM. A rule table maps error_type -> explanation template, and a
separate patch function per error type edits ONLY the failing line.
Deterministic rules are testable and cannot hallucinate.
"""
import ast
import difflib
import re


class NLPExplainer:

    # ------------------------------------------------------------------
    # 1. EXPLANATION (IR dict -> plain English)
    # ------------------------------------------------------------------
    def explain(self, ir):
        etype = ir.get("error_type") or "UnknownError"
        msg = ir.get("error_message") or ""
        line = ir.get("line_number")
        name = self._quoted(msg)   # first 'quoted' token in the message, if any
        where = f" on line {line}" if line else ""

        rules = {
            "NameError": (
                f"Using the name '{name}'{where} before it is defined.",
                "Python cannot find any variable, function or import with that name in scope.",
                "Define it before use, or correct the spelling if it is a typo.",
            ),
            "TypeError": (
                f"Mixing incompatible data types{where}.",
                f"An operation was applied to types that do not support it ({msg}).",
                "Convert one operand so the types match, e.g. str(5) or int('5').",
            ),
            "ZeroDivisionError": (
                f"Dividing by zero{where}.",
                "The denominator evaluates to 0, which is undefined in arithmetic.",
                "Check that the denominator is not zero before dividing.",
            ),
            "SyntaxError": (
                f"Invalid code structure{where}.",
                f"The parser could not read the statement ({msg}). "
                "A common cause is a missing ':' or an unclosed bracket.",
                "Correct the syntax, e.g. end if/for/while/def lines with ':'.",
            ),
            "KeyError": (
                f"Looking up a dictionary key that does not exist{where}.",
                f"The key '{name}' is not present in the dictionary.",
                "Use dict.get(key) or check 'key in dict' first.",
            ),
            "IndexError": (
                f"Accessing a list position that does not exist{where}.",
                "The index is larger than the last valid position (len - 1).",
                "Check the index against len(list) before accessing it.",
            ),
            "ValueError": (
                f"Passing a value of the right type but invalid content{where}.",
                f"The value could not be converted or accepted ({msg}).",
                "Validate the input, or wrap the conversion in try/except.",
            ),
            "ModuleNotFoundError": (
                f"Importing a module '{name}' that is not installed or misspelled{where}.",
                "Python searched its path and found no module with that name.",
                "Install it (pip install <name>) or fix the module name.",
            ),
        }
        mistake, reason, fix = rules.get(etype, (
            f"A {etype} occurred{where}.",
            msg or "No further detail was provided by the interpreter.",
            "Read the traceback from the bottom up and inspect the failing line.",
        ))
        return f"Mistake: {mistake}\nReason: {reason}\nFix: {fix}"

    # ------------------------------------------------------------------
    # 2. AUTO-FIX (IR + source -> patched source)
    # ------------------------------------------------------------------
    def generate_fixed_code(self, ir, code):
        etype = ir.get("error_type")
        line_no = ir.get("line_number")
        lines = code.split("\n")
        if not line_no or line_no > len(lines):
            return code

        idx = line_no - 1
        patcher = getattr(self, f"_fix_{etype}", None)
        if patcher is None:
            return code                      # no rule for this error: change nothing

        patched = list(lines)
        patcher(ir, patched, idx)
        new_code = "\n".join(patched)

        # SAFETY GATE (mini patch validator): a patch must still parse.
        # Never hand back code that is more broken than what we received.
        try:
            ast.parse(new_code)
        except SyntaxError:
            return code
        return new_code

    # ---- helpers ------------------------------------------------------
    @staticmethod
    def _quoted(msg):
        m = re.search(r"'([^']+)'", msg or "")
        return m.group(1) if m else ""

    @staticmethod
    def _split_comment(line):
        """Separate code from trailing '# comment' so regexes don't touch comments."""
        i = line.find("#")
        return (line[:i], line[i:]) if i != -1 else (line, "")

    @staticmethod
    def _indent(line):
        return line[: len(line) - len(line.lstrip())]

    # ---- one patch function per error type ----------------------------
    def _fix_SyntaxError(self, ir, lines, i):
        code, comment = self._split_comment(lines[i])
        stripped = code.strip()
        openers = ("if ", "elif ", "else", "for ", "while ", "def ", "class ",
                   "try", "except", "finally", "with ")
        if stripped.startswith(openers) and not stripped.endswith(":"):
            lines[i] = code.rstrip() + ":" + (" " + comment if comment else "")

    def _fix_NameError(self, ir, lines, i):
        bad = ir.get("error_variable") or self._quoted(ir.get("error_message"))
        if not bad:
            return
        # Levenshtein-style typo repair: closest name already used in the program.
        # difflib's ratio is a similarity score; cutoff 0.75 avoids wild guesses.
        candidates = [v for v in ir.get("variables_used", []) if v != bad]
        match = difflib.get_close_matches(bad, candidates, n=1, cutoff=0.75)
        if match:
            code, comment = self._split_comment(lines[i])
            lines[i] = re.sub(rf"\b{re.escape(bad)}\b", match[0], code) + comment
        else:
            # No plausible typo target: declare it but do NOT invent a value.
            lines.insert(i, f"{self._indent(lines[i])}{bad} = None  # TODO: define a real value")

    def _fix_ZeroDivisionError(self, ir, lines, i):
        code, comment = self._split_comment(lines[i])
        code = re.sub(r"(\w+)\s*(//|/|%)\s*(\w+)",
                      r"(\1 \2 \3 if \3 != 0 else 0)", code, count=1)
        # Honest patch: the guard stops the crash but SUBSTITUTES 0, which can hide a logic
        # bug. Mark the line so a human reviews it instead of trusting the silent default.
        note = "  # [auto-fix] guarded division, yields 0 if denominator is 0"
        lines[i] = code.rstrip() + note + (" " + comment if comment else "")

    def _fix_TypeError(self, ir, lines, i):
        code, comment = self._split_comment(lines[i])
        # 'text' + 5  ->  'text' + str(5)
        code = re.sub(r"(['\"][^'\"]*['\"])\s*\+\s*(\w+)", r"\1 + str(\2)", code, count=1)
        lines[i] = code + comment

    def _fix_KeyError(self, ir, lines, i):
        code, comment = self._split_comment(lines[i])
        # d['b'] -> d.get('b')
        code = re.sub(r"(\w+)\[(['\"][^'\"]+['\"])\]", r"\1.get(\2)", code, count=1)
        lines[i] = code + comment

    def _fix_IndexError(self, ir, lines, i):
        code, comment = self._split_comment(lines[i])
        # lst[10] -> (lst[10] if len(lst) > 10 else None)
        code = re.sub(r"(\w+)\[(\d+)\]",
                      r"(\1[\2] if len(\1) > \2 else None)", code, count=1)
        lines[i] = code + comment

    def _fix_ModuleNotFoundError(self, ir, lines, i):
        ind = self._indent(lines[i])
        code, comment = self._split_comment(lines[i])
        mod = self._quoted(ir.get("error_message"))
        # Guard the import instead of deleting it, so the program can continue.
        lines[i] = (f"{ind}try:\n{ind}    {code.strip()}\n"
                    f"{ind}except ImportError:\n{ind}    {mod} = None  # module unavailable")