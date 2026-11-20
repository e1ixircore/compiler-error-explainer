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
    "UnknownType": "The compiler does not recognize this type or template name.",
    "MissingTemplateArgs": "A C++ template class (like std::vector) was used without specifying its type in <...>.",
    "MissingSemicolon": "A C++ statement or declaration is missing its terminating semicolon (;).",
    "MissingClassSemicolon": "A struct, class, or enum definition is missing its required semicolon after '}'.",
    "MissingBrace": "An opening curly brace '{' was never closed with '}'.",
    "ExtraBrace": "There is an extra closing curly brace '}' that does not match any open block.",
    "MissingParen": "An opening parenthesis '(' was never closed with ')'.",
    "TypeMismatch": "A value of one C++ type was used where an incompatible type was expected.",
    "WrongStreamOperator": "The stream arrows (<< / >>) point the wrong way for cout/cin.",
    "InvalidMainSignature": "In standard C++, the main() function must have return type int.",
    "DivisionByZero": "A number is divided by zero, which is undefined behaviour in C++.",
    "ArrayOutOfBounds": "An array was accessed at an index past the end of its allocated size.",
    "MissingReturn": "A non-void function reaches its end without returning a value.",
    "VoidReturnValue": "A void function tried to return a value.",
    "AssignmentInCondition": "A single '=' (assignment) was used in a condition where '==' (comparison) was likely meant.",
    "UninitializedVariable": "A variable is read before it has been given an initial value.",
    "PointerMemberAccess": "Dot '.' was used on a pointer instead of the arrow '->' operator.",
    "ValueMemberAccess": "Arrow '->' was used on a plain object instead of the dot '.' operator.",
    "ConstModification": "The code tried to modify a variable declared as const (read-only).",
    "ConstUninitialized": "A const variable was declared without giving it an initial value.",
    "InvalidDereference": "The dereference operator '*' was applied to a non-pointer value.",
    "InvalidSubscript": "Array indexing '[...]' was used on a variable that is not an array, pointer, or vector.",
    "NotCallable": "Function call parentheses '(...)' were used on something that is not a function.",
    "WrongArgumentCount": "A function was called with too few or too many arguments.",
    "MisplacedLoopControl": "'break' or 'continue' was used outside of any loop (or switch for break).",
    "NotAssignable": "The left side of '=' is not a variable that can be assigned to.",
    "IncompleteType": "A type was used before its full definition or header was included.",
    "ReferenceBinding": "A non-const reference (&) cannot bind to a temporary value or incompatible type.",
    "DuplicateCase": "Two case labels in the same switch statement have the same value.",
    "NoMatchingFunction": "No function overload matches the argument types or count passed in the call.",
    "NoSuchMember": "An object or struct was asked for a field or method that it does not have.",
    "Redefinition": "The same variable or function name was defined more than once in the same scope.",
    "SyntaxError": "The line violates C++ syntax rules so the compiler cannot parse it.",
    "CompileTimeout": "Compilation took too long and was stopped.",
    "CompileError": "The C++ compiler rejected this statement.",
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
    """Return (mistake, reason, fix) tuple for a C++ diagnostic with actionable change instructions."""
    etype = diagnostic.get("error_type") or "CompileError"
    msg = diagnostic.get("error_message") or diagnostic.get("message") or ""
    line = diagnostic.get("line_number") or diagnostic.get("line")
    where = f" on line {line}" if line else ""
    name = diagnostic.get("name") or ""
    header = diagnostic.get("header") or ""
    sug = diagnostic.get("suggestion") or ""
    exp_t = diagnostic.get("expected_type") or ""
    act_t = diagnostic.get("actual_type") or ""
    notes = diagnostic.get("notes") or []
    snippet = (diagnostic.get("snippet") or "").strip()

    # Build a concrete TypeMismatch explanation using exact types from the compiler message
    tm_detail = f" (expected '{exp_t}', got '{act_t}')" if (exp_t and act_t) else ""
    tm_fix = (
        f"Change the value on line {line} so it has type '{exp_t}' instead of '{act_t}', or change the variable/function type to '{act_t}'."
        if (exp_t and act_t)
        else "Change the value to match the declared type, or convert explicitly (e.g. std::to_string(num) for int→string, std::stoi(str) for string→int)."
    )
    if exp_t in ("int", "double", "float", "long") and "char" in act_t:
        art = "an" if exp_t.startswith(("i", "a", "e", "o", "u")) else "a"
        tm_fix = f"Replace the quoted text with {art} {exp_t} number (e.g. 0 or 42), or change the variable/return type from '{exp_t}' to 'std::string'."
    elif "string" in exp_t and act_t in ("int", "double", "float", "long"):
        tm_fix = f"Wrap the number in std::to_string(...) so it becomes a std::string, or change the variable type to '{act_t}'."

    # Parse expected vs actual argument counts for WrongArgumentCount
    arg_m = re.search(r"expected (?:at least |at most )?(\d+), have (\d+)", msg)
    arg_detail = f" (expected {arg_m.group(1)} argument(s), but {arg_m.group(2)} were given)" if arg_m else ""
    arg_fix = (
        f"Pass exactly {arg_m.group(1)} argument(s) inside the parentheses instead of {arg_m.group(2)}."
        if arg_m
        else "Check the function definition above and pass the exact number of arguments it declares."
    )

    rules = {
        "MissingHeaderFile": (
            f"The header file '{name}' could not be found{where}." if name else f"A header file could not be found{where}.",
            f"The compiler looked for <{name}> and could not locate it."
            + (f" Did you mean <{sug}>?" if sug else " The header name may be misspelled or not installed."),
            f"Change '#include <{name}>' to '#include <{sug}>'." if sug else "Fix the spelling of the header file name inside #include <...>.",
        ),
        "MissingInclude": (
            f"'{name}' is used{where}, but its standard header <{header}> is not included." if name and header
            else f"A standard library name is used{where} without its required #include.",
            "In C++, standard library features live in separate headers (such as <iostream>, <vector>, <string>, <algorithm>, <cmath>) that must be included at the top of the file.",
            f"Add '#include <{header}>' at the top of the file." if header else "Add the required #include <...> header at the top of the file.",
        ),
        "MissingStdPrefix": (
            f"'{name}' is used{where} without the 'std::' namespace prefix.",
            f"Standard C++ names like '{name}' live inside the 'std' namespace, so the compiler does not recognize '{name}' by itself.",
            f"Replace '{name}' with '{sug or ('std::' + name)}' on line {line} (e.g. std::{name}).",
        ),
        "UnknownType": (
            f"The type name '{name}'{where} is not recognized by the compiler." if name else f"An unknown type name was used{where}.",
            f"C++ does not have a built-in type called '{name}'."
            + (f" It looks like a typo for '{sug}'." if sug else " It may be misspelled, missing 'std::', or missing its #include/struct definition."),
            (f"Replace '{name}' with '{sug}' on line {line}." if sug else f"Check the spelling of '{name}', add 'std::' if it is a standard library type, or define the struct/class above."),
        ),
        "MissingTemplateArgs": (
            f"The template class '{name}'{where} is missing its type argument in '<...>'." if name else f"A template class is missing its '<Type>' arguments{where}.",
            "C++ containers like std::vector, std::array, and std::map need to know what type of elements they hold inside angle brackets.",
            f"Specify the element type in angle brackets, e.g. change '{name or 'std::vector'}' to '{name or 'std::vector'}<int>'.",
        ),
        "UndeclaredIdentifier": (
            f"The name '{name}'{where} has not been declared.",
            "C++ requires every variable and function to be declared with a type before it is used. Either it was never declared or it is misspelled."
            + (f" Did you mean '{sug}'?" if sug else ""),
            (f"Rename '{name}' to '{sug}' on line {line}." if sug else f"Click '+ Line above L{line}' and declare '{name}' with its type first, e.g. 'int {name or 'x'} = 0;'."),
        ),
        "MissingSemicolon": (
            f"A semicolon (;) is missing{where}.",
            "Every C++ statement and variable declaration must end with a semicolon (;).",
            f"Add ';' at the end of line {line} (or at the end of the previous statement if the error points to the start of line {line}).",
        ),
        "MissingClassSemicolon": (
            f"A semicolon (;) is missing after the closing '}}' of a struct/class/enum{where}.",
            "Unlike functions and if-blocks, C++ requires a semicolon immediately after the closing brace '}' of every struct, class, or enum definition.",
            f"Change '}}' to '}};' on line {line}.",
        ),
        "MissingBrace": (
            f"A closing curly brace '}}' is missing{where}.",
            "An opening '{' for a function, loop, or if-block does not have a matching '}'.",
            "Add the missing '}' at the end of the block.",
        ),
        "ExtraBrace": (
            f"There is an extra closing curly brace '}}'{where}.",
            "This '}' does not match any open '{' block.",
            f"Delete the extra '}}' on line {line}, or add the missing opening '{{' earlier in the block.",
        ),
        "MissingParen": (
            f"A closing parenthesis ')' is missing{where}.",
            "An opening '(' in a condition, expression, or function call was not closed.",
            f"Add the missing ')' on line {line} to close the expression.",
        ),
        "TypeMismatch": (
            f"Type mismatch{where}{tm_detail}.",
            f"C++ is strictly typed and cannot automatically convert between these types. Compiler detail: {msg}",
            tm_fix,
        ),
        "WrongStreamOperator": (
            f"The stream arrows (<< or >>) are facing the wrong way{where}.",
            "std::cout uses '<<' (sending data out to the screen), whereas std::cin uses '>>' (reading data in from the keyboard).",
            f"On line {line}, change '>>' to '<<' for std::cout/std::cerr, or change '<<' to '>>' for std::cin.",
        ),
        "InvalidMainSignature": (
            f"main() has an invalid return type{where}.",
            "Standard C++ requires main() to return 'int' so the operating system receives an exit status (0 for success).",
            f"Change the declaration on line {line} to 'int main()' and make sure it ends with 'return 0;'.",
        ),
        "DivisionByZero": (
            f"The expression divides by zero{where}.",
            "Division or modulo by 0 is undefined behaviour in C++ and will crash the program at runtime (SIGFPE).",
            f"Change the divisor on line {line} to a non-zero value, or guard it with 'if (d != 0)' before dividing.",
        ),
        "ArrayOutOfBounds": (
            f"An array index is out of bounds{where}.",
            f"C++ arrays are 0-indexed (valid indices for size N are 0 to N-1). Compiler detail: {msg}",
            f"Reduce the index on line {line} so it is strictly less than the array's length, or use std::vector::at() for bounds checking.",
        ),
        "MissingReturn": (
            f"A non-void function reaches its end without returning a value{where}.",
            "Every code path in a function declared with a return type (like int, double, or std::string) must execute a 'return <value>;' statement.",
            f"Add a 'return <value>;' statement matching the function's return type before the closing '}}' on line {line}.",
        ),
        "VoidReturnValue": (
            f"A 'void' function tried to return a value{where}.",
            "Functions declared with return type 'void' do not return data to their caller.",
            f"Either remove the value on line {line} (write just 'return;'), or change the function's return type from 'void' to the type being returned (e.g. 'int').",
        ),
        "AssignmentInCondition": (
            f"A single '=' (assignment) was used inside a condition{where}.",
            "Single '=' overwrites the variable instead of comparing values. Conditions almost always need '==' (equality check).",
            f"Replace '=' with '==' inside the condition on line {line}.",
        ),
        "UninitializedVariable": (
            f"Variable '{name}' is read before being initialized{where}." if name else f"A variable is read before being initialized{where}.",
            "Unlike Python, C++ does NOT automatically set local variables to 0 — reading an uninitialized variable produces unpredictable garbage values.",
            f"Give '{name or 'the variable'}' an initial value where it is declared, e.g. 'int {name or 'x'} = 0;'.",
        ),
        "PointerMemberAccess": (
            f"Dot '.' was used on a pointer{where} instead of '->'.",
            f"In C++, pointers to structs/objects (type '{name or 'T*'}') must use the arrow operator '->' to access members, while plain objects use '.'.",
            f"Replace '.' with '->' on line {line} (e.g. change 'ptr.field' to 'ptr->field').",
        ),
        "ValueMemberAccess": (
            f"Arrow '->' was used on a non-pointer object{where} instead of '.'.",
            f"The variable on line {line} is a direct object (type '{name or 'T'}'), not a pointer, so it uses the dot '.' operator.",
            f"Replace '->' with '.' on line {line} (e.g. change 'obj->field' to 'obj.field').",
        ),
        "ConstModification": (
            f"Code tried to modify the 'const' variable '{name}'{where}." if name else f"Code tried to modify a 'const' (read-only) variable{where}.",
            "Variables marked 'const' cannot be reassigned after initialization.",
            f"Either remove the 'const' keyword from '{name or 'the variable'}'s declaration if it is meant to change, or delete the reassignment on line {line}.",
        ),
        "ConstUninitialized": (
            f"A 'const' variable was declared without an initial value{where}.",
            "Because a 'const' variable can never be assigned later, C++ requires you to give it a value right when you declare it.",
            f"Add '= <value>' to the declaration on line {line} (e.g. 'const int limit = 10;').",
        ),
        "InvalidDereference": (
            f"The dereference operator '*' was used on a non-pointer{where} (type '{act_t or 'non-pointer'}').",
            "The unary '*' operator reads the value a pointer points to, so it only works on pointer types like 'int*'.",
            f"Remove the leading '*' on line {line} to use the value directly, or declare the variable as a pointer (e.g. 'int* ptr = &x;').",
        ),
        "InvalidSubscript": (
            f"Bracket indexing '[...]' was used on a non-array variable{where}.",
            "Only arrays, pointers, std::vector, std::string, or std::map support '[index]' lookup.",
            f"Remove '[...]' on line {line} if the variable is a single number, or change its declaration to an array or std::vector.",
        ),
        "NotCallable": (
            f"Tried to call a non-function value of type '{act_t or 'unknown'}' using '(...)'{where}.",
            "Parentheses '(...)' after a name tell C++ to call a function, but this name refers to a plain variable (or a variable shadowing a function).",
            f"Remove the '(...)' call on line {line}, use '*' if you meant multiplication (e.g. 'a * (b + c)'), or rename the variable if it hides a function.",
        ),
        "WrongArgumentCount": (
            f"Function called with the wrong number of arguments{where}{arg_detail}.",
            f"The number of arguments passed in the call does not match the function's parameter list. Compiler detail: {msg}",
            arg_fix,
        ),
        "MisplacedLoopControl": (
            f"'break' or 'continue' was used outside of a loop{where}.",
            "'continue' can only be used inside a for/while/do-while loop, and 'break' can only be used inside a loop or switch statement.",
            f"Move the statement on line {line} inside a loop, or replace it with 'return;' if you meant to exit the function.",
        ),
        "NotAssignable": (
            f"The left side of '=' on line {line} cannot be assigned to.",
            "Only a modifiable variable (an lvalue) can appear on the left side of '=' — not a literal like '5' or a temporary expression like 'a + b'.",
            f"Put the variable name on the left of '=' (e.g. 'x = 5;'), or change '=' to '==' if you meant to compare values.",
        ),
        "IncompleteType": (
            f"An incomplete type was used{where}.",
            f"The compiler knows the name exists (forward-declared), but hasn't seen its full definition or #include header yet. Compiler detail: {msg}",
            "Include the header that defines this type (such as <fstream>, <sstream>, or <string>) or move the full struct/class definition above this line.",
        ),
        "ReferenceBinding": (
            f"A non-const reference cannot bind to this value{where}.",
            f"In C++, a non-const reference ('T&') must bind to a real variable of the exact same type, not a literal or temporary value. Compiler detail: {msg}",
            f"Pass a declared variable instead of a literal/expression on line {line}, or change the reference parameter to 'const {exp_t or 'auto'}&'.",
        ),
        "DuplicateCase": (
            f"Duplicate 'case' value in switch statement{where}.",
            "Every 'case' label inside the same switch block must have a unique constant value.",
            f"Change or remove the duplicate 'case' label on line {line}.",
        ),
        "NoMatchingFunction": (
            f"No matching function call for '{name}'{where}." if name else f"No matching function call was found{where}.",
            f"The arguments passed do not match any available overload of this function. Compiler detail: {msg}"
            + (f" Note: {notes[0]}" if notes else ""),
            (f"Did you mean '{sug}'? Replace '{name}' with '{sug}'." if sug else f"Check the number and types of arguments passed on line {line} against the function's parameter list."),
        ),
        "NoSuchMember": (
            f"The object has no member named '{name}'{where}." if name else f"A nonexistent member was accessed{where}.",
            f"The struct or class does not define a field or method named '{name}'."
            + (f" Did you mean '{sug}'?" if sug else f" Compiler detail: {msg}"),
            (f"Rename '.{name}' to '.{sug}' on line {line}." if sug else f"Check the exact spelling of '{name}' in the struct/class definition (e.g. std::vector uses '.push_back()' and '.size()')."),
        ),
        "Redefinition": (
            f"'{name}' is defined more than once{where}." if name else f"A name is redefined in the same scope{where}.",
            "C++ does not allow two variables or functions with the same name and signature in the same block.",
            f"Remove the type keyword on line {line} if you meant to reassign '{name}' (e.g. '{name} = ...;' instead of 'int {name} = ...;'), or rename the variable.",
        ),
        "SyntaxError": (
            f"C++ syntax error{where}: {msg}",
            f"The compiler could not parse '{snippet}' as valid C++." if snippet else f"Compiler detail: {msg}",
            f"Check line {line} (and the line right above it) for a missing semicolon ';', unmatched parenthesis/brace, or misplaced operator.",
        ),
        "CompileTimeout": (
            "Compilation exceeded the time limit.",
            msg or "The code triggered an excessively long compile (such as deep template recursion).",
            "Simplify templates or constexpr loops.",
        ),
    }
    if etype in rules:
        return rules[etype]

    # Smart fallback for any remaining unrecognized C++ compiler error:
    # Never give a generic "Review the compiler diagnostic" — extract the exact token and note!
    quoted = re.findall(r"['\u2018]([^'\u2019]+)['\u2019]", msg)
    tok_hint = f" around '{quoted[0]}'" if quoted else ""
    note_hint = f" ({notes[0]})" if notes else ""
    fix_hint = (
        f"Replace '{quoted[0]}' with '{sug}' on line {line}."
        if (quoted and sug)
        else (
            f"Check '{quoted[0]}' on line {line}: verify its type, declaration, and syntax against the compiler detail above."
            if quoted
            else f"Inspect '{snippet}' on line {line} and fix the syntax or type issue noted by the compiler."
        )
    )
    return (
        f"C++ compiler error{tok_hint}{where}: {msg}",
        f"The compiler rejected '{snippet}'{note_hint}." if snippet else (msg or "The compiler rejected this line."),
        fix_hint,
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

    # 17. PointerMemberAccess (`ptr.field` -> `ptr->field`)
    if error_type == "PointerMemberAccess":
        code_part, comment_part = _split_cpp_comment(line)
        if isinstance(col, int) and 1 <= col <= len(code_part):
            # Find '.' near col
            dot_pos = code_part.find(".", max(0, col - 3))
            if dot_pos < 0:
                dot_pos = code_part.rfind(".", 0, col + 2)
            if dot_pos >= 0:
                lines[line_index] = code_part[:dot_pos] + "->" + code_part[dot_pos + 1:] + comment_part
                return "\n".join(lines)
        new_code = _sub_masked(code_part, r"(?<=\w)\.(?=[A-Za-z_])", lambda m, g: "->", count=1)
        if new_code != code_part:
            lines[line_index] = new_code + comment_part
            return "\n".join(lines)

    # 18. ValueMemberAccess (`obj->field` -> `obj.field`)
    if error_type == "ValueMemberAccess":
        code_part, comment_part = _split_cpp_comment(line)
        if isinstance(col, int) and 1 <= col <= len(code_part):
            arr_pos = code_part.find("->", max(0, col - 3))
            if arr_pos < 0:
                arr_pos = code_part.rfind("->", 0, col + 3)
            if arr_pos >= 0:
                lines[line_index] = code_part[:arr_pos] + "." + code_part[arr_pos + 2:] + comment_part
                return "\n".join(lines)
        new_code = _sub_masked(code_part, r"->", lambda m, g: ".", count=1)
        if new_code != code_part:
            lines[line_index] = new_code + comment_part
            return "\n".join(lines)

    # 19. MissingClassSemicolon (`}` -> `};` after struct/class/enum)
    if error_type == "MissingClassSemicolon":
        code_part, comment_part = _split_cpp_comment(line)
        pos = code_part.rfind("}")
        if pos >= 0 and not code_part[pos + 1:].strip().startswith(";"):
            lines[line_index] = code_part[:pos + 1] + ";" + code_part[pos + 1:] + comment_part
            return "\n".join(lines)

    # 20. UnknownType with clear typo suggestion (e.g. `strng` -> `std::string`)
    if error_type == "UnknownType" and name and suggestion:
        replacement = _replace_identifier(line, name, suggestion, count=0)
        if replacement is not None:
            lines[line_index] = replacement
            bare = suggestion.replace("std::", "")
            if suggestion.startswith("std::") and bare in STD_SYMBOL_HEADERS:
                _insert_include(lines, STD_SYMBOL_HEADERS[bare])
            return "\n".join(lines)

    # 21. NoSuchMember with clear typo suggestion (e.g. `v.push_bak(1)` -> `v.push_back(1)`)
    if error_type == "NoSuchMember" and name and suggestion:
        code_part, comment_part = _split_cpp_comment(line)
        new_code = _sub_masked(
            code_part,
            rf"(\.|->)\s*{re.escape(name)}(?!\w)",
            lambda m, g: f"{g(1)}{suggestion}",
            count=1,
        )
        if new_code != code_part:
            lines[line_index] = new_code + comment_part
            return "\n".join(lines)

    return code
