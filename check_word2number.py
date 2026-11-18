from app import repair_loop, verify_fix
from error_extractor import extract_error


CASES = (
    ("seventeen", 17),
    ("one hundred and five", 105),
)

for words, expected in CASES:
    code = f"age = int({words!r})\nprint(age)\n"
    initial = extract_error(code)
    fixed, history = repair_loop(code)
    assert initial["error_type"] == "ValueError", (words, initial)
    assert f"int({expected})" in fixed, (words, fixed)
    assert history[0]["result"] == "patched", (words, history)
    assert verify_fix(code, fixed)["verdict"] == "VERIFIED", words
    print(f"PASS int({words!r}) -> {expected}")

numeric = "age = int('42')\nprint(age)\n"
fixed, _ = repair_loop(numeric)
assert fixed == numeric, fixed
print("PASS valid numeric string remains unchanged")
