"""
INTENTIONALLY BUGGY TEST FILE 2
More than 500 lines. Contains exactly 10 deliberate defect sites.
The remaining functions are valid filler/test utilities.
Do not use this file in production.
"""
from __future__ import annotations
from typing import Any

def add_numbers(a: int, b: int) -> int:
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    return a * b

def get_length(items: list[Any]) -> int:
    return len(items)

def safe_average(items: list[float]) -> float:
    if not items:
        return 0.0
    return sum(items) / len(items)

def make_record(identifier: int, label: str) -> dict[str, Any]:
    return {"id": identifier, "label": label}

def clean_text(value: str) -> str:
    return value.strip().lower()

def is_even(value: int) -> bool:
    return value % 2 == 0

def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))

def safe_get(items: list[Any], index: int, default: Any = None) -> Any:
    if 0 <= index < len(items):
        return items[index]
    return default

def safe_lookup(record: dict[str, Any], key: str, default: Any = None) -> Any:
    return record.get(key, default)

def safe_division(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return a / b

# ---- Deliberate defects: 10 total in this file ----

def defect_01_type_mismatch() -> int:
    return "wrong type"  # DEFECT 1: static type mismatch

def defect_02_undefined_name() -> int:
    return missing_variable_02  # DEFECT 2: undefined name

def defect_03_division_by_zero() -> float:
    return 10 / 0  # DEFECT 3: runtime ZeroDivisionError

def defect_04_bad_index(items: list[int]) -> int:
    return items[len(items)]  # DEFECT 4: runtime IndexError

def defect_05_bad_conversion() -> int:
    return int("not-a-number")  # DEFECT 5: runtime ValueError

def defect_06_missing_key(record: dict[str, int]) -> int:
    return record["absent"]  # DEFECT 6: runtime KeyError

def defect_07_bad_attribute(value: Any) -> str:
    return value.upper()  # DEFECT 7: runtime AttributeError for integer input

def defect_08_wrong_argument_type() -> int:
    return len(123)  # DEFECT 8: runtime TypeError

def defect_09_type_assignment() -> str:
    count: int = "many"  # DEFECT 9: static type mismatch
    return count

def defect_10_undefined_function() -> Any:
    return calculate_missing_total()  # DEFECT 10: undefined function

def run_safe_examples() -> None:
    print(add_numbers(2, 3))
    print(multiply_numbers(2.5, 4.0))
    print(safe_average([2.0, 4.0, 6.0]))
    print(make_record(1, "sample"))

if __name__ == "__main__":
    run_safe_examples()

# The following generated utilities increase file length without adding defects.

def second_utility_001(value: int, offset: int = 1) -> int:
    """Clean utility function 001."""
    result = value + offset + 1
    return result

def second_utility_002(value: int, offset: int = 2) -> int:
    """Clean utility function 002."""
    result = value + offset + 2
    return result

def second_utility_003(value: int, offset: int = 3) -> int:
    """Clean utility function 003."""
    result = value + offset + 3
    return result

def second_utility_004(value: int, offset: int = 4) -> int:
    """Clean utility function 004."""
    result = value + offset + 4
    return result

def second_utility_005(value: int, offset: int = 5) -> int:
    """Clean utility function 005."""
    result = value + offset + 0
    return result

def second_utility_006(value: int, offset: int = 6) -> int:
    """Clean utility function 006."""
    result = value + offset + 1
    return result

def second_utility_007(value: int, offset: int = 7) -> int:
    """Clean utility function 007."""
    result = value + offset + 2
    return result

def second_utility_008(value: int, offset: int = 8) -> int:
    """Clean utility function 008."""
    result = value + offset + 3
    return result

def second_utility_009(value: int, offset: int = 0) -> int:
    """Clean utility function 009."""
    result = value + offset + 4
    return result

def second_utility_010(value: int, offset: int = 1) -> int:
    """Clean utility function 010."""
    result = value + offset + 0
    return result

def second_utility_011(value: int, offset: int = 2) -> int:
    """Clean utility function 011."""
    result = value + offset + 1
    return result

def second_utility_012(value: int, offset: int = 3) -> int:
    """Clean utility function 012."""
    result = value + offset + 2
    return result

def second_utility_013(value: int, offset: int = 4) -> int:
    """Clean utility function 013."""
    result = value + offset + 3
    return result

def second_utility_014(value: int, offset: int = 5) -> int:
    """Clean utility function 014."""
    result = value + offset + 4
    return result

def second_utility_015(value: int, offset: int = 6) -> int:
    """Clean utility function 015."""
    result = value + offset + 0
    return result

def second_utility_016(value: int, offset: int = 7) -> int:
    """Clean utility function 016."""
    result = value + offset + 1
    return result

def second_utility_017(value: int, offset: int = 8) -> int:
    """Clean utility function 017."""
    result = value + offset + 2
    return result

def second_utility_018(value: int, offset: int = 0) -> int:
    """Clean utility function 018."""
    result = value + offset + 3
    return result

def second_utility_019(value: int, offset: int = 1) -> int:
    """Clean utility function 019."""
    result = value + offset + 4
    return result

def second_utility_020(value: int, offset: int = 2) -> int:
    """Clean utility function 020."""
    result = value + offset + 0
    return result

def second_utility_021(value: int, offset: int = 3) -> int:
    """Clean utility function 021."""
    result = value + offset + 1
    return result

def second_utility_022(value: int, offset: int = 4) -> int:
    """Clean utility function 022."""
    result = value + offset + 2
    return result

def second_utility_023(value: int, offset: int = 5) -> int:
    """Clean utility function 023."""
    result = value + offset + 3
    return result

def second_utility_024(value: int, offset: int = 6) -> int:
    """Clean utility function 024."""
    result = value + offset + 4
    return result

def second_utility_025(value: int, offset: int = 7) -> int:
    """Clean utility function 025."""
    result = value + offset + 0
    return result

def second_utility_026(value: int, offset: int = 8) -> int:
    """Clean utility function 026."""
    result = value + offset + 1
    return result

def second_utility_027(value: int, offset: int = 0) -> int:
    """Clean utility function 027."""
    result = value + offset + 2
    return result

def second_utility_028(value: int, offset: int = 1) -> int:
    """Clean utility function 028."""
    result = value + offset + 3
    return result

def second_utility_029(value: int, offset: int = 2) -> int:
    """Clean utility function 029."""
    result = value + offset + 4
    return result

def second_utility_030(value: int, offset: int = 3) -> int:
    """Clean utility function 030."""
    result = value + offset + 0
    return result

def second_utility_031(value: int, offset: int = 4) -> int:
    """Clean utility function 031."""
    result = value + offset + 1
    return result

def second_utility_032(value: int, offset: int = 5) -> int:
    """Clean utility function 032."""
    result = value + offset + 2
    return result

def second_utility_033(value: int, offset: int = 6) -> int:
    """Clean utility function 033."""
    result = value + offset + 3
    return result

def second_utility_034(value: int, offset: int = 7) -> int:
    """Clean utility function 034."""
    result = value + offset + 4
    return result

def second_utility_035(value: int, offset: int = 8) -> int:
    """Clean utility function 035."""
    result = value + offset + 0
    return result

def second_utility_036(value: int, offset: int = 0) -> int:
    """Clean utility function 036."""
    result = value + offset + 1
    return result

def second_utility_037(value: int, offset: int = 1) -> int:
    """Clean utility function 037."""
    result = value + offset + 2
    return result

def second_utility_038(value: int, offset: int = 2) -> int:
    """Clean utility function 038."""
    result = value + offset + 3
    return result

def second_utility_039(value: int, offset: int = 3) -> int:
    """Clean utility function 039."""
    result = value + offset + 4
    return result

def second_utility_040(value: int, offset: int = 4) -> int:
    """Clean utility function 040."""
    result = value + offset + 0
    return result

def second_utility_041(value: int, offset: int = 5) -> int:
    """Clean utility function 041."""
    result = value + offset + 1
    return result

def second_utility_042(value: int, offset: int = 6) -> int:
    """Clean utility function 042."""
    result = value + offset + 2
    return result

def second_utility_043(value: int, offset: int = 7) -> int:
    """Clean utility function 043."""
    result = value + offset + 3
    return result

def second_utility_044(value: int, offset: int = 8) -> int:
    """Clean utility function 044."""
    result = value + offset + 4
    return result

def second_utility_045(value: int, offset: int = 0) -> int:
    """Clean utility function 045."""
    result = value + offset + 0
    return result

def second_utility_046(value: int, offset: int = 1) -> int:
    """Clean utility function 046."""
    result = value + offset + 1
    return result

def second_utility_047(value: int, offset: int = 2) -> int:
    """Clean utility function 047."""
    result = value + offset + 2
    return result

def second_utility_048(value: int, offset: int = 3) -> int:
    """Clean utility function 048."""
    result = value + offset + 3
    return result

def second_utility_049(value: int, offset: int = 4) -> int:
    """Clean utility function 049."""
    result = value + offset + 4
    return result

def second_utility_050(value: int, offset: int = 5) -> int:
    """Clean utility function 050."""
    result = value + offset + 0
    return result

def second_utility_051(value: int, offset: int = 6) -> int:
    """Clean utility function 051."""
    result = value + offset + 1
    return result

def second_utility_052(value: int, offset: int = 7) -> int:
    """Clean utility function 052."""
    result = value + offset + 2
    return result

def second_utility_053(value: int, offset: int = 8) -> int:
    """Clean utility function 053."""
    result = value + offset + 3
    return result

def second_utility_054(value: int, offset: int = 0) -> int:
    """Clean utility function 054."""
    result = value + offset + 4
    return result

def second_utility_055(value: int, offset: int = 1) -> int:
    """Clean utility function 055."""
    result = value + offset + 0
    return result

def second_utility_056(value: int, offset: int = 2) -> int:
    """Clean utility function 056."""
    result = value + offset + 1
    return result

def second_utility_057(value: int, offset: int = 3) -> int:
    """Clean utility function 057."""
    result = value + offset + 2
    return result

def second_utility_058(value: int, offset: int = 4) -> int:
    """Clean utility function 058."""
    result = value + offset + 3
    return result

def second_utility_059(value: int, offset: int = 5) -> int:
    """Clean utility function 059."""
    result = value + offset + 4
    return result

def second_utility_060(value: int, offset: int = 6) -> int:
    """Clean utility function 060."""
    result = value + offset + 0
    return result

def second_utility_061(value: int, offset: int = 7) -> int:
    """Clean utility function 061."""
    result = value + offset + 1
    return result

def second_utility_062(value: int, offset: int = 8) -> int:
    """Clean utility function 062."""
    result = value + offset + 2
    return result

def second_utility_063(value: int, offset: int = 0) -> int:
    """Clean utility function 063."""
    result = value + offset + 3
    return result

def second_utility_064(value: int, offset: int = 1) -> int:
    """Clean utility function 064."""
    result = value + offset + 4
    return result

def second_utility_065(value: int, offset: int = 2) -> int:
    """Clean utility function 065."""
    result = value + offset + 0
    return result

def second_utility_066(value: int, offset: int = 3) -> int:
    """Clean utility function 066."""
    result = value + offset + 1
    return result

def second_utility_067(value: int, offset: int = 4) -> int:
    """Clean utility function 067."""
    result = value + offset + 2
    return result

def second_utility_068(value: int, offset: int = 5) -> int:
    """Clean utility function 068."""
    result = value + offset + 3
    return result

def second_utility_069(value: int, offset: int = 6) -> int:
    """Clean utility function 069."""
    result = value + offset + 4
    return result

def second_utility_070(value: int, offset: int = 7) -> int:
    """Clean utility function 070."""
    result = value + offset + 0
    return result

def second_utility_071(value: int, offset: int = 8) -> int:
    """Clean utility function 071."""
    result = value + offset + 1
    return result

def second_utility_072(value: int, offset: int = 0) -> int:
    """Clean utility function 072."""
    result = value + offset + 2
    return result

def second_utility_073(value: int, offset: int = 1) -> int:
    """Clean utility function 073."""
    result = value + offset + 3
    return result

def second_utility_074(value: int, offset: int = 2) -> int:
    """Clean utility function 074."""
    result = value + offset + 4
    return result

def second_utility_075(value: int, offset: int = 3) -> int:
    """Clean utility function 075."""
    result = value + offset + 0
    return result

def second_utility_076(value: int, offset: int = 4) -> int:
    """Clean utility function 076."""
    result = value + offset + 1
    return result

def second_utility_077(value: int, offset: int = 5) -> int:
    """Clean utility function 077."""
    result = value + offset + 2
    return result

def second_utility_078(value: int, offset: int = 6) -> int:
    """Clean utility function 078."""
    result = value + offset + 3
    return result

def second_utility_079(value: int, offset: int = 7) -> int:
    """Clean utility function 079."""
    result = value + offset + 4
    return result

def second_utility_080(value: int, offset: int = 8) -> int:
    """Clean utility function 080."""
    result = value + offset + 0
    return result

def second_utility_081(value: int, offset: int = 0) -> int:
    """Clean utility function 081."""
    result = value + offset + 1
    return result

def second_utility_082(value: int, offset: int = 1) -> int:
    """Clean utility function 082."""
    result = value + offset + 2
    return result

def second_utility_083(value: int, offset: int = 2) -> int:
    """Clean utility function 083."""
    result = value + offset + 3
    return result

def second_utility_084(value: int, offset: int = 3) -> int:
    """Clean utility function 084."""
    result = value + offset + 4
    return result

def second_utility_085(value: int, offset: int = 4) -> int:
    """Clean utility function 085."""
    result = value + offset + 0
    return result

def second_utility_086(value: int, offset: int = 5) -> int:
    """Clean utility function 086."""
    result = value + offset + 1
    return result

def second_utility_087(value: int, offset: int = 6) -> int:
    """Clean utility function 087."""
    result = value + offset + 2
    return result

def second_utility_088(value: int, offset: int = 7) -> int:
    """Clean utility function 088."""
    result = value + offset + 3
    return result

def second_utility_089(value: int, offset: int = 8) -> int:
    """Clean utility function 089."""
    result = value + offset + 4
    return result

def second_utility_090(value: int, offset: int = 0) -> int:
    """Clean utility function 090."""
    result = value + offset + 0
    return result

def second_utility_091(value: int, offset: int = 1) -> int:
    """Clean utility function 091."""
    result = value + offset + 1
    return result

def second_utility_092(value: int, offset: int = 2) -> int:
    """Clean utility function 092."""
    result = value + offset + 2
    return result

def second_utility_093(value: int, offset: int = 3) -> int:
    """Clean utility function 093."""
    result = value + offset + 3
    return result

def second_utility_094(value: int, offset: int = 4) -> int:
    """Clean utility function 094."""
    result = value + offset + 4
    return result

def second_utility_095(value: int, offset: int = 5) -> int:
    """Clean utility function 095."""
    result = value + offset + 0
    return result

def second_utility_096(value: int, offset: int = 6) -> int:
    """Clean utility function 096."""
    result = value + offset + 1
    return result

def second_utility_097(value: int, offset: int = 7) -> int:
    """Clean utility function 097."""
    result = value + offset + 2
    return result

def second_utility_098(value: int, offset: int = 8) -> int:
    """Clean utility function 098."""
    result = value + offset + 3
    return result

def second_utility_099(value: int, offset: int = 0) -> int:
    """Clean utility function 099."""
    result = value + offset + 4
    return result

def second_utility_100(value: int, offset: int = 1) -> int:
    """Clean utility function 100."""
    result = value + offset + 0
    return result

def second_utility_101(value: int, offset: int = 2) -> int:
    """Clean utility function 101."""
    result = value + offset + 1
    return result

def second_utility_102(value: int, offset: int = 3) -> int:
    """Clean utility function 102."""
    result = value + offset + 2
    return result

def second_utility_103(value: int, offset: int = 4) -> int:
    """Clean utility function 103."""
    result = value + offset + 3
    return result

def second_utility_104(value: int, offset: int = 5) -> int:
    """Clean utility function 104."""
    result = value + offset + 4
    return result

def second_utility_105(value: int, offset: int = 6) -> int:
    """Clean utility function 105."""
    result = value + offset + 0
    return result

def second_utility_106(value: int, offset: int = 7) -> int:
    """Clean utility function 106."""
    result = value + offset + 1
    return result

def second_utility_107(value: int, offset: int = 8) -> int:
    """Clean utility function 107."""
    result = value + offset + 2
    return result

def second_utility_108(value: int, offset: int = 0) -> int:
    """Clean utility function 108."""
    result = value + offset + 3
    return result

def second_utility_109(value: int, offset: int = 1) -> int:
    """Clean utility function 109."""
    result = value + offset + 4
    return result

def second_utility_110(value: int, offset: int = 2) -> int:
    """Clean utility function 110."""
    result = value + offset + 0
    return result

