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
    # 1. EXPLANATION (IR dict -> plain English for a BEGINNER)
    #    Rule of thumb for every template: no compiler jargon (no "operand", "denominator",
    #    "scope", "AST"). If a term is needed, explain it with an everyday comparison.
    # ------------------------------------------------------------------
    # One-line definition of each error, shown under the ORIGINAL error name in the UI.
    # The name itself (NameError, KeyError...) is never renamed: students will meet it in real tracebacks.
    MEANINGS = {
        "NameError": "Python found a name (a variable or function) that it does not recognise.",
        "TypeError": "An operation was used on a kind of data that does not support it.",
        "ZeroDivisionError": "A number was divided by zero, which has no answer.",
        "SyntaxError": "The code breaks Python's writing rules, so Python cannot read it.",
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
        name = self._quoted(msg)   # first 'quoted' token in the message, if any
        where = f" on line {line}" if line else ""
        sug = ir.get("suggestion")

        # TypeError: only the text + number case gets the specific wording; others stay generic.
        if "concatenate" in msg or "can only" in msg:
            type_rule = (
                f"You are joining text and a number with + {where.strip()}.".replace("  ", " "),
                "In Python, text (like 'Total: ') and numbers (like 5) are different kinds of data, "
                "and + cannot glue them together.",
                "Turn the number into text with str(), e.g. 'Total: ' + str(5).",
            )
        else:
            type_rule = (
                f"Two different kinds of data are being combined{where}.",
                f"Python does not allow this operation on these data types. Python said: {msg}",
                "Convert one of the values so both are the same kind, e.g. str(5) or int('5').",
            )

        rules = {
            "NameError": (
                f"The name '{name}'{where} has not been created yet.",
                "Python only knows a variable once you give it a value. Either it was never created, "
                "or it is spelled differently from where you created it."
                + (f" Did you mean '{sug}'?" if sug else ""),
                (f"Change it to '{sug}' if that was your intention, otherwise create " if sug else "Create ")
                + "the variable before this line, e.g. " + (name or "x") + " = 0.",
            ),
            "TypeError": type_rule,
            "ZeroDivisionError": (
                f"The program divides a number by zero{where}.",
                "Dividing by 0 has no answer in maths, so Python stops with an error.",
                "Make sure the number you divide by is never 0, for example check it with an if first.",
            ),
            "SyntaxError": (
                f"Python cannot understand line {line}." if line else "Python cannot understand one of your lines.",
                f"It is written in a way Python's grammar does not allow (Python said: {msg}). "
                "The most common causes are a missing ':' at the end of an if/for/while/def line, "
                "or a bracket or quote that was opened but never closed.",
                "Check the end of this line and the line above it for a missing ':' or a missing closing bracket.",
            ),
            "KeyError": (
                f"You asked a dictionary for a key it does not have{where}.",
                f"A dictionary works like a phone book: looking up '{name}' fails if there is no entry with that name.",
                "Check the spelling of the key, or use dict.get(key), which gives None instead of crashing.",
            ),
            "IndexError": (
                f"You asked for a list item that does not exist{where}.",
                "List positions start at 0, so a list with 3 items has positions 0, 1 and 2. "
                "This position is past the end of the list.",
                "Use a position smaller than len(your_list), or check the length first.",
            ),
            "ValueError": (
                f"The value has the right type but the wrong content{where}.",
                f"For example, int('hello') fails because 'hello' is not a number. Python said: {msg}",
                "Check the value before converting it, or wrap the conversion in try/except.",
            ),
            "ModuleNotFoundError": (
                f"Python cannot find a library called '{name}'{where}.",
                "Either the library is not installed on this computer, or its name is misspelled.",
                f"Check the spelling, or install it with: pip install {name}",
            ),
            "TimeoutError": (
                "The program ran for more than 5 seconds and was stopped.",
                "This usually means a loop that never ends, such as while True without a way to break out.",
                "Make sure every loop has a condition that eventually becomes false, or a break.",
            ),
            "NestingError": (
                "The code is nested too deeply to be analysed safely.",
                "Too many brackets or operations are stacked inside each other.",
                "Split the long expression into several smaller lines.",
            ),
        }
        mistake, reason, fix = rules.get(etype, (
            f"A {etype} occurred{where}.",
            msg or "Python gave no further detail.",
            "Read the error message from the bottom up and look at the line it points to.",
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
        except SyntaxError as e:
            # Python reports ONE syntax error at a time. A patch to a SyntaxError is still accepted when the
            # file does not parse yet, as long as the first error MOVED LATER (= real progress, and it can
            # never loop). Any other patch that breaks parsing is rejected.
            if etype == "SyntaxError" and e.lineno and e.lineno > line_no:
                return new_code
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