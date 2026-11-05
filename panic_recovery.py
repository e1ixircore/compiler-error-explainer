# panic_recovery.py - PANIC-MODE error recovery for the parser stage.
# Problem: ast.parse() raises on the FIRST SyntaxError and gives no AST, so a file with
# 3 syntax errors would report only one.
# Panic mode (classic compiler technique): on an error, ENTER PANIC, DISCARD the bad
# statement up to a SYNCHRONISING POINT (here: the end of the line, because Python
# statements are newline-terminated), substitute a harmless placeholder, then RESUME
# parsing. Every error found on the way is recorded.
# The recovered text is ONLY used to keep parsing; it is never executed or saved.
import ast

# Lines that open a block. Replacing one with `pass` would orphan the indented body
# below it, causing a bogus 'unexpected indent', so we keep a valid header instead.
OPENERS = ("if ", "elif ", "else", "for ", "while ", "def ", "class ",
           "try", "except", "finally", "with ")


def _indent(line):
    return line[: len(line) - len(line.lstrip())]


def collect_syntax_errors(code, max_errors=20):
    """Returns (errors, recovered_code). errors = list of IR-shaped dicts.
    Termination: at most max_errors rounds, and a line that fails twice stops the loop."""
    lines, errors, failed_lines = code.split("\n"), [], set()
    recovered = False
    for _ in range(max_errors):
        try:
            ast.parse("\n".join(lines))
            recovered = True
            break                                  # parse succeeded: panic is over
        except SyntaxError as e:
            ln = e.lineno
            if not ln or ln > len(lines):
                break
            if ln in failed_lines:
                # Same line fails again after we neutralised it: the REAL culprit is an
                # earlier line (e.g. an unclosed '(' whose damage shows up lower down).
                # Walk back to the previous line we have not touched yet.
                while ln in failed_lines and ln > 1:
                    ln -= 1
                if ln in failed_lines:
                    break                          # cannot synchronise: give up honestly
            else:
                errors.append({"error_type": "IndentationError" if isinstance(e, IndentationError)
                               else "SyntaxError",
                               "error_message": e.msg, "line_number": ln,
                               "column": (e.offset or 1) - 1})
            failed_lines.add(ln)
            i, bad = ln - 1, lines[ln - 1]

            # --- SYNCHRONISE: choose the smallest edit that lets the parser resume ---
            if e.msg.startswith("expected an indented block"):
                # error is reported on the line AFTER the opener: give the opener a body
                prev = next((j for j in range(i - 1, -1, -1) if lines[j].strip()), None)
                base = _indent(lines[prev]) if prev is not None else ""
                lines.insert(i, base + "    pass")
                failed_lines = {x + (x >= ln) for x in failed_lines}   # shift after insert
            elif e.msg.startswith("unexpected indent"):
                prev = next((j for j in range(i - 1, -1, -1) if lines[j].strip()), None)
                lines[i] = (_indent(lines[prev]) if prev is not None else "") + bad.strip()
            elif bad.strip().startswith(OPENERS):
                lines[i] = _indent(bad) + "if True:"         # keep the block structure valid
            else:
                lines[i] = _indent(bad) + "pass"             # discard the bad statement
    return errors, "\n".join(lines), recovered


if __name__ == "__main__":
    demo = "def f():\n    if True\n        print('a')\n    x = (1 +\n    return x\nprint('ok'\nfor i in range(3)\n    pass\n"
    errs, fixed, ok = collect_syntax_errors(demo)
    for e in errs:
        print(e)
    print("resumed parsing:", ok)