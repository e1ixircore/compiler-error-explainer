"""Rule-based C++ explainer and auto-fixer (deterministic, no LLM, comment/string-aware)."""
import difflib
import re

from cpp_extractor import ALL_STD_HEADERS, STD_SYMBOL_HEADERS

SAFE_HEADERS = set(ALL_STD_HEADERS)

MEANINGS = {
    "MissingHeaderFile": "The compiler could not find the header file named in #include.",
    "MissingInclude": "A C++ standard library feature was used without including its header.",
    "MissingStdPrefix": "A standard library name was written without its std:: prefix.",
    "UndeclaredIdentifier": "The compiler encountered a variable or function name it has not seen declared.",
    "MissingSemicolon": "A C++ statement or declaration is missing its terminating semicolon (;).",
    "MissingBrace": "An opening curly brace '{' was never closed with '}'.",
    "ExtraBrace": "There is an extra closing curly brace '}' that does not match any open block.",
    "MissingParen": "An opening parenthesis '(' was never closed with ')'.",
    "TypeMismatch": "A value of one C++ type was used where an incompatible type was expected.",
    "WrongStreamOperator": "The stream arrows (<< / >>) point the wrong way for cout/cin.",
    "InvalidMainSignature": "In standard C++, the main() function must have return type int.",
    "DivisionByZero": "A number is divided by zero, which is undefined behaviour in C++.",
    "ArrayOutOfBounds": "An array was accessed at an index past the end of its allocated size.",
    "MissingReturn": "A non-void function reaches its end without returning a value.",
    "AssignmentInCondition": "A single '=' (assignment) was used in a condition where '==' (comparison) was likely meant.",
    "UninitializedVariable": "A variable is read before it has been given an initial value.",
    "NoMatchingFunction": "No function overload matches the argument types or count passed in the call.",
    "NoSuchMember": "An object or struct was asked for a field or method that it does not have.",
    "Redefinition": "The same variable or function name was defined more than once in the same scope.",
    "SyntaxError": "The line violates C++ syntax rules so the compiler cannot parse it.",
    "CompileTimeout": "Compilation took too long and was stopped.",
    "CompileError": "The C++ compiler rejected the code.",
}


def meaning(etype):
    return MEANINGS.get(etype, "The C++ compiler reported an error in this code.")


# ----------------------------------------------------------------------
# Lexical helpers: mask comments and string/char literals so edits never touch them
# ----------------------------------------------------------------------
def _mask_cpp(code):
    """Return a same-length string where C++ comments and string/char literals are '\\x00' (newlines preserved)."""
    out, i, n = [], 0, len(code)
    while i < n:
        c = code[i]
        if c == "/" and i + 1 < n and code[i + 1] == "/":
            j = code.find("\n", i)
            j = n if j < 0 else j
            out.append("\x00" * (j - i))
            i = j
            continue
        if c == "/" and i + 1 < n and code[i + 1] == "*":
            j = code.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join("\n" if ch == "\n" else "\x00" for ch in code[i:j]))
            i = j
            continue
        if c in ('"', "'"):
            q = c
            out.append("\x00")
            i += 1
            while i < n:
                if code[i] == "\\" and i + 1 < n:
                    out.append("\n" if code[i + 1] == "\n" else "\x00")
                    i += 2
                    continue
                if code[i] == q:
                    out.append("\x00")
                    i += 1
                    break
                out.append("\n" if code[i] == "\n" else "\x00")
                i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _split_cpp_comment(line):
    """Split a single line into (code_part, trailing_line_comment), ignoring '//' inside strings."""
    masked = _mask_cpp(line)
    # Find first '//' in original line where masked is '\x00' and original is '//'
    i = 0
    while i < len(line) - 1:
        if line[i:i + 2] == "//" and masked[i] == "\x00":
            # Verify it wasn't inside a string literal by checking if an unmasked quote preceded it
            if i == 0 or masked[i - 1] != "\x00" or line[i - 1] in (' ', '\t'):
                return line[:i], line[i:]
        i += 1
    return line, ""


def _sub_masked(line, pattern, repl, count=0):
    """Regex-substitute on the masked text of `line`, copying edits into the original line."""
    masked = _mask_cpp(line)
    out, last, n = [], 0, 0
    for m in re.finditer(pattern, masked):
        out.append(line[last:m.start()])
        out.append(repl(m, lambda k, m=m: line[m.start(k):m.end(k)]))
        last = m.end()
        n += 1
        if count and n >= count:
            break
    out.append(line[last:])
    return "".join(out)


def _replace_identifier(line, old, new, count=1):
    """Replace identifier `old` with `new` outside comments and string literals."""
    if not old or not new or not re.fullmatch(r"[A-Za-z_]\w*", old):
        return None
    if not re.fullmatch(r"(?:[A-Za-z_]\w*::)*[A-Za-z_]\w*", new):
        return None
    # Avoid matching `std::old` or `obj.old` or `ptr->old`
    pat = rf"(?<![\w.:>]){re.escape(old)}(?!\w)"
    replaced = _sub_masked(line, pat, lambda m, g: new, count=count)
    return replaced if replaced != line else None


def _indent(line):
    return line[: len(line) - len(line.lstrip())]


# ----------------------------------------------------------------------
# Explanations (beginner-friendly Mistake / Reason / Fix)
# ----------------------------------------------------------------------
def explain(diagnostic):
    """Return (mistake, reason, fix) tuple for a C++ diagnostic."""
    etype = diagnostic.get("error_type") or "CompileError"
    msg = diagnostic.get("error_message") or diagnostic.get("message") or ""
    line = diagnostic.get("line_number") or diagnostic.get("line")
    where = f" on line {line}" if line else ""
    name = diagnostic.get("name") or ""
    header = diagnostic.get("header") or ""
    sug = diagnostic.get("suggestion") or ""

    rules = {
        "MissingHeaderFile": (
            f"The header file '{name}' could not be found{where}." if name else f"A header file could not be found{where}.",
            f"The compiler looked for <{name}> and could not locate it."
            + (f" Did you mean <{sug}>?" if sug else " The header name may be misspelled or not installed."),
            f"Change the include to #include <{sug}>." if sug else "Check the spelling of the header file name and include paths.",
        ),
        "MissingInclude": (
            f"'{name}' is used{where}, but its standard header <{header}> is not included." if name and header
            else f"A standard library name is used{where} without its required #include.",
            "In C++, standard library features live in separate headers (such as <iostream>, <vector>, <string>) that must be included at the top of the file.",
            f"Add #include <{header}> at the top of the file." if header else "Include the standard library header that defines this name.",
        ),
        "MissingStdPrefix": (
            f"'{name}' is used{where} without the std:: namespace prefix.",
            "Standard C++ names like cout, cin, endl, string, and vector live inside namespace std.",
            f"Write {sug or ('std::' + name)} instead of {name} (or add using std::{name};).",
        ),
        "UndeclaredIdentifier": (
            f"The name '{name}'{where} has not been declared.",
            "C++ requires every variable and function to be declared with a type before it is used. Either it was never declared or it is misspelled."
            + (f" Did you mean '{sug}'?" if sug else ""),
            (f"Rename '{name}' to '{sug}'." if sug else f"Declare '{name}' with its type before this line, e.g. int {name or 'x'} = 0;."),
        ),
        "MissingSemicolon": (
            f"A semicolon (;) is missing{where}.",
            "Almost every statement and declaration in C++ must end with a semicolon.",
            "Add ';' at the end of the statement (or on the line right above if the error appeared at the start of this line).",
        ),
        "MissingBrace": (
            f"A closing curly brace '}}' is missing{where}.",
            "An opening '{' for a function, loop, or if-block does not have a matching '}'.",
            "Add the missing '}' at the end of the block.",
        ),
        "ExtraBrace": (
            f"There is an extra closing curly brace '}}'{where}.",
            "This '}' does not match any open '{' block.",
            "Remove the extra '}' or check if an opening '{' is missing above.",
        ),
        "MissingParen": (
            f"A closing parenthesis ')' is missing{where}.",
            "An opening '(' in a condition, expression, or function call was not closed.",
            "Add the missing ')' to close the expression.",
        ),
        "TypeMismatch": (
            f"Incompatible types are being combined or assigned{where}.",
            f"C++ is strictly typed and cannot automatically convert between these types. Compiler said: {msg}",
            "Use a matching type for the variable/return value, or convert explicitly (e.g. std::to_string(...) or std::stoi(...)).",
        ),
        "WrongStreamOperator": (
            f"The stream arrows (<< or >>) are facing the wrong way{where}.",
            "std::cout uses << (inserting into output), whereas std::cin uses >> (extracting from input).",
            "Use << with std::cout/std::cerr and >> with std::cin.",
        ),
        "InvalidMainSignature": (
            f"main() has an invalid return type{where}.",
            "Standard C++ requires main() to return int so the operating system receives an exit status.",
            "Change the signature to 'int main()' and return 0 at the end.",
        ),
        "DivisionByZero": (
            f"The expression divides by zero{where}.",
            "Division or modulo by 0 is undefined behaviour in C++ and will crash the program at runtime (SIGFPE).",
            "Check that the divisor is not 0 before dividing, e.g. (d != 0 ? a / d : 0).",
        ),
        "ArrayOutOfBounds": (
            f"An array index is out of bounds{where}.",
            f"Accessing past the end of a fixed-size C++ array causes undefined behaviour or a crash. Compiler said: {msg}",
            "Keep array indices strictly between 0 and size - 1 (or use std::vector::at() for bounds checking).",
        ),
        "MissingReturn": (
            f"A non-void function reaches its end without a return statement{where}.",
            "Every path through a function declared with a return type (like int or double) must return a value.",
            "Add a return statement with a value of the declared return type before the closing '}'.",
        ),
        "AssignmentInCondition": (
            f"A single '=' was used inside a condition{where}.",
            "Single '=' assigns a value instead of comparing two values. You almost certainly meant '=='.",
            "Replace '=' with '==' inside the if/while condition.",
        ),
        "UninitializedVariable": (
            f"Variable '{name}' is used before being initialized{where}." if name else f"A variable is used before being initialized{where}.",
            "Reading an uninitialized local variable in C++ yields garbage memory (undefined behaviour).",
            f"Give '{name or 'the variable'}' an initial value when declaring it, e.g. int {name or 'x'} = 0;.",
        ),
        "NoMatchingFunction": (
            f"No matching function call was found{where}.",
            f"The arguments passed do not match any available function signature. Compiler said: {msg}",
            "Check the number and types of arguments passed to the function.",
        ),
        "NoSuchMember": (
            f"The object has no member named '{name}'{where}." if name else f"A nonexistent member was accessed{where}.",
            f"The struct or class does not define this field or method. Compiler said: {msg}",
            "Check the spelling of the member name and the type of the object.",
        ),
        "Redefinition": (
            f"'{name}' is defined more than once{where}." if name else f"A name is redefined in the same scope{where}.",
            "C++ does not allow two variables with the same name in the same block.",
            "Remove the duplicate declaration or rename one of the variables.",
        ),
        "SyntaxError": (
            f"The compiler could not parse C++ syntax{where}.",
            f"Compiler said: {msg}",
            "Check this line and the line directly above for missing punctuation, operators, or brackets.",
        ),
        "CompileTimeout": (
            "Compilation exceeded the time limit.",
            msg or "The code triggered an excessively long compile (such as deep template recursion).",
            "Simplify templates or constexpr loops.",
        ),
    }
    return rules.get(
        etype,
        (
            f"The C++ compiler reported an error{where}.",
            msg or "The compiler rejected this line.",
            "Review the compiler diagnostic and adjust the code.",
        ),
    )


def hides_crash(etype, patch):
    """True if the patch substitutes a stand-in value (0, clamped index, TODO stub)."""
    text = " ".join(t for _, t in patch)
    return (
        etype in ("DivisionByZero", "ArrayOutOfBounds", "MissingReturn")
        or "TODO:" in text
        or "[auto-fix]" in text
    )


# ----------------------------------------------------------------------
# Auto-fix helpers
# ----------------------------------------------------------------------
def _insert_include(lines, header):
    include = f"#include <{header}>"
    if any(re.match(rf"^\s*#\s*include\s*<{re.escape(header)}>\s*$", l) for l in lines):
        return False
    insert_at = 0
    for idx, line in enumerate(lines):
        if re.match(r"^\s*#\s*(include|pragma)\b", line):
            insert_at = idx + 1
        elif line.strip() and not line.lstrip().startswith("//") and insert_at:
            break
    lines.insert(insert_at, include)
    return True


def _cpp_default_for_type(ctype):
    t = re.sub(r"\b(?:const|static|inline|unsigned|signed|long|short)\b", "", ctype or "").strip()
    if t in ("int", "size_t", "int64_t", "int32_t"):
        return "0"
    if t in ("double", "float"):
        return "0.0"
    if t == "bool":
        return "false"
    if t == "char":
        return "'\\0'"
    if "string" in t:
        return '""'
    return "{}"


def _find_enclosing_func_return_type(lines, line_index):
    """Walk backwards from a closing '}' to find the enclosing function's return type."""
    depth = 0
    for j in range(line_index, -1, -1):
        masked = _mask_cpp(lines[j])
        for ch in reversed(masked):
            if ch == "}":
                depth += 1
            elif ch == "{":
                depth -= 1
                if depth == 0:
                    # Check this line (and line above) for a function signature
                    sig = lines[j]
                    if not re.search(r"[A-Za-z_]\w*\s*\(", sig) and j > 0:
                        sig = lines[j - 1] + " " + sig
                    m = re.match(
                        r"^\s*((?:const\s+|static\s+|inline\s+|unsigned\s+|long\s+)*"
                        r"(?:std::)?[A-Za-z_]\w*(?:<[^>]+>)?\s*[\*&]?)\s+[A-Za-z_]\w*\s*\(",
                        sig,
                    )
                    if m:
                        ret = m.group(1).strip()
                        if ret not in ("if", "for", "while", "switch", "else", "return"):
                            return ret
                    return None
    return None


def _needs_semicolon(line):
    code, _ = _split_cpp_comment(line)
    s = code.rstrip()
    if not s:
        return False
    if s.startswith("#"):
        return False
    if s.endswith((";", "{", "}", ":", "\\", ",")):
        return False
    return True


def apply_fix(code, diagnostic):
    """Apply a focused, high-confidence edit for one C++ diagnostic; returns patched code or original."""
    lines = code.split("\n")
    line_number = diagnostic.get("line") or diagnostic.get("line_number")
    line_index = line_number - 1 if isinstance(line_number, int) else -1
    col = diagnostic.get("column")
    error_type = diagnostic.get("error_type")
    message = diagnostic.get("message") or diagnostic.get("error_message") or ""
    name = diagnostic.get("name")
    header = diagnostic.get("header")
    suggestion = diagnostic.get("suggestion")
    notes = diagnostic.get("notes") or []

    # 1. MissingHeaderFile (typo like #include <iostrem> -> #include <iostream>)
    if error_type == "MissingHeaderFile" and 0 <= line_index < len(lines):
        target_hdr = suggestion
        if not target_hdr and name:
            close = difflib.get_close_matches(name, ALL_STD_HEADERS, n=1, cutoff=0.7)
            target_hdr = close[0] if close else None
        if target_hdr and name:
            new_line = re.sub(
                rf"(#\s*include\s*[<\"]){re.escape(name)}([>\"])",
                rf"\g<1>{target_hdr}\g<2>",
                lines[line_index],
                count=1,
            )
            if new_line != lines[line_index]:
                lines[line_index] = new_line
                return "\n".join(lines)
        return code

    # 2. MissingInclude (#include <iostream>, <vector>, <string>, ...)
    if error_type == "MissingInclude":
        hdr = header or (STD_SYMBOL_HEADERS.get(name) if name else None)
        if hdr in SAFE_HEADERS and _insert_include(lines, hdr):
            return "\n".join(lines)
        return code

    if not 0 <= line_index < len(lines):
        # MissingBrace at EOF may report one line past the end.
        if error_type == "MissingBrace":
            masked = _mask_cpp(code)
            if masked.count("{") > masked.count("}"):
                return code.rstrip() + "\n}\n"
        return code

    line = lines[line_index]

    # 3. MissingStdPrefix (cout -> std::cout, works even with strings/comments on the line)
    if error_type == "MissingStdPrefix" and name:
        target = suggestion if (suggestion and suggestion.startswith("std::")) else f"std::{name}"
        replacement = _replace_identifier(line, name, target, count=0)
        if replacement is not None:
            lines[line_index] = replacement
            return "\n".join(lines)

    # 4. UndeclaredIdentifier (typo rename or known std symbol; truly undeclared names are explain-only)
    if error_type == "UndeclaredIdentifier" and name:
        if suggestion:
            replacement = _replace_identifier(line, name, suggestion, count=0)
            if replacement is not None:
                lines[line_index] = replacement
                return "\n".join(lines)
        # Check if it's a known std symbol whose header is missing or needs std::
        if name in STD_SYMBOL_HEADERS:
            hdr = STD_SYMBOL_HEADERS[name]
            if _insert_include(lines, hdr):
                return "\n".join(lines)
            replacement = _replace_identifier(line, name, f"std::{name}", count=0)
            if replacement is not None:
                lines[line_index] = replacement
                return "\n".join(lines)
        return code

    # 5. MissingSemicolon (handles current line OR previous line when reported `before ...`, preserves comments)
    if error_type == "MissingSemicolon":
        target_idx = line_index
        if "before" in message and line_index > 0:
            # Find previous non-empty code line
            prev = next((j for j in range(line_index - 1, -1, -1) if _split_cpp_comment(lines[j])[0].strip()), None)
            if prev is not None and _needs_semicolon(lines[prev]):
                target_idx = prev
        if _needs_semicolon(lines[target_idx]):
            code_part, comment_part = _split_cpp_comment(lines[target_idx])
            lines[target_idx] = code_part.rstrip() + ";" + (("  " + comment_part.lstrip()) if comment_part else "")
            return "\n".join(lines)
        return code

    # 6. MissingBrace (works for BOTH GCC "expected '}' at end of input" and Apple Clang "expected '}'")
    if error_type == "MissingBrace":
        masked = _mask_cpp(code)
        if masked.count("{") > masked.count("}"):
            return code.rstrip() + "\n}\n"
        return code

    # 7. ExtraBrace
    if error_type == "ExtraBrace":
        code_part, comment_part = _split_cpp_comment(line)
        if code_part.strip() == "}":
            del lines[line_index]
            return "\n".join(lines)
        pos = code_part.rfind("}")
        if pos >= 0:
            lines[line_index] = code_part[:pos] + code_part[pos + 1:] + comment_part
            return "\n".join(lines)
        return code

    # 8. MissingParen
    if error_type == "MissingParen":
        code_part, comment_part = _split_cpp_comment(line)
        masked = _mask_cpp(code_part)
        opens = masked.count("(") - masked.count(")")
        if opens > 0:
            closers = ")" * opens
            # Insert before trailing '{' or ';' if present, else at end of code_part
            m = re.search(r"\s*(\{|;)\s*$", masked)
            if m:
                ins = m.start()
                new_code = code_part[:ins].rstrip() + closers + code_part[ins:]
            elif isinstance(col, int) and 1 <= col <= len(code_part) + 1:
                ins = col - 1
                new_code = code_part[:ins].rstrip() + closers + code_part[ins:]
            else:
                new_code = code_part.rstrip() + closers
            lines[line_index] = new_code + (("  " + comment_part.lstrip()) if comment_part else "")
            return "\n".join(lines)
        return code

    # 9. InvalidMainSignature (void main() -> int main())
    if error_type == "InvalidMainSignature":
        new_line = _sub_masked(line, r"\b(?:void|float|double|char|bool)\s+(main\s*\()", lambda m, g: f"int {g(1)}", count=1)
        if new_line != line:
            lines[line_index] = new_line
            return "\n".join(lines)
        return code

    # 10. WrongStreamOperator (cout >> x -> cout << x; cin << x -> cin >> x)
    if error_type == "WrongStreamOperator":
        masked = _mask_cpp(line)
        if re.search(r"\b(?:cout|cerr|clog)\b", masked) and ">>" in masked:
            new_line = _sub_masked(line, r">>", lambda m, g: "<<", count=0)
            if new_line != line:
                lines[line_index] = new_line
                return "\n".join(lines)
        if re.search(r"\bcin\b", masked) and "<<" in masked:
            new_line = _sub_masked(line, r"<<", lambda m, g: ">>", count=0)
            if new_line != line:
                lines[line_index] = new_line
                return "\n".join(lines)
        return code

    # 11-13. DivisionByZero, ArrayOutOfBounds, MissingReturn:
    # Intent-ambiguous logic defects — explain-only (do not substitute fake 0s or clamped indices).
    if error_type in ("DivisionByZero", "ArrayOutOfBounds", "MissingReturn"):
        return code

    # 14. AssignmentInCondition (if (x = 5) -> if (x == 5))
    if error_type == "AssignmentInCondition":
        code_part, comment_part = _split_cpp_comment(line)
        new_code = _sub_masked(code_part, r"(?<![=!<>+\-*/%&|^])=(?!=)", lambda m, g: "==", count=1)
        if new_code != code_part:
            lines[line_index] = new_code + comment_part
            return "\n".join(lines)
        return code

    # 15. UninitializedVariable (initialize local variable declaration)
    if error_type == "UninitializedVariable" and name:
        # Walk backwards to find `T name;` declaration
        decl_pat = re.compile(rf"^(\s*(?:(?:unsigned|signed|long|short)\s+)*(?:int|double|float|bool|char|size_t)\s+{re.escape(name)})\s*;")
        for j in range(line_index, -1, -1):
            code_part, comment_part = _split_cpp_comment(lines[j])
            m = decl_pat.match(code_part)
            if m:
                lines[j] = m.group(1) + " = 0;" + (("  " + comment_part.lstrip()) if comment_part else "")
                return "\n".join(lines)
        return code

    # 16. TypeMismatch: only lossless/unambiguous conversions (`int n = "42";`, `std::string s = 42;`).
    # Non-numeric mismatches like `return "wrong";` or `int count = "many";` are explain-only.
    if error_type == "TypeMismatch":
        code_part, comment_part = _split_cpp_comment(line)
        # Case A: returning a numeric string literal from a numeric function (`return "42";` -> `return 42;`)
        m_ret = re.search(r"cannot initialize return object of type '([^']+)' with .*'const char\[\d+\]'", message)
        if m_ret:
            target_t = m_ret.group(1).strip()
            str_m = re.search(r'\breturn\s+"([^"]*)"\s*;', code_part)
            if str_m:
                lit = str_m.group(1).strip()
                repl = None
                if target_t in ("int", "long", "short") and re.fullmatch(r"-?\d+", lit):
                    repl = lit
                elif target_t in ("double", "float") and re.fullmatch(r"-?\d+(\.\d+)?", lit):
                    repl = lit
                if repl is not None:
                    new_code = re.sub(r'(\breturn\s+)"[^"]*"(\s*;)', rf"\g<1>{repl}\g<2>", code_part, count=1)
                    if new_code != code_part:
                        lines[line_index] = new_code + (("  " + comment_part.lstrip()) if comment_part else "")
                        return "\n".join(lines)

        # Case B: initializing numeric variable with a numeric string literal (`int n = "42";` -> `int n = 42;`)
        m_var = re.search(r"cannot initialize a variable of type '([^']+)' with .*'const char\[\d+\]'", message)
        if m_var:
            target_t = m_var.group(1).strip()
            str_m = re.search(r'=\s*"([^"]*)"\s*;', code_part)
            if str_m:
                lit = str_m.group(1).strip()
                repl = None
                if target_t in ("int", "long", "short") and re.fullmatch(r"-?\d+", lit):
                    repl = lit
                elif target_t in ("double", "float") and re.fullmatch(r"-?\d+(\.\d+)?", lit):
                    repl = lit
                if repl is not None:
                    new_code = re.sub(r'(=\s*)"[^"]*"(\s*;)', rf"\g<1>{repl}\g<2>", code_part, count=1)
                    if new_code != code_part:
                        lines[line_index] = new_code + (("  " + comment_part.lstrip()) if comment_part else "")
                        return "\n".join(lines)

        # Case C: initializing std::string with a number (`std::string s = 42;`)
        if re.search(r"no viable conversion from '(int|double|float|long)' to '.*string'", message):
            new_code = re.sub(r"(=\s*)([^;]+)(\s*;)", r"\g<1>std::to_string(\g<2>)\g<3>", code_part, count=1)
            if new_code != code_part:
                lines[line_index] = new_code + comment_part
                _insert_include(lines, "string")
                return "\n".join(lines)

    return code
