"""
INTENTIONALLY BUGGY TEST FILE 1
Purpose: exercise static analyzers and runtime error detection with balanced patchable and unfixable defects.
This file contains deliberate defects. Do not use in production.
Run with: python test_upload_buggy_test_file_1.py
"""
from __future__ import annotations
import math
import json
from pathlib import Path
from typing import Any, List, Dict, Optional

# --- Demonstration Functions ---

def safe_divide(a: float, b: float) -> float:
    """Deliberate division by zero (unfixable: manual fix)."""
    return a / b

def get_item(values: list[int], index: int) -> int:
    """Deliberate index error (unfixable: manual fix)."""
    return values[index]

def parse_word_number(value: str) -> int:
    """English number word conversion (auto-patchable: int(42))."""
    return int("forty-two")

def counter_pattern_demo(key: str) -> int:
    """Counter increment pattern (auto-patchable: dict.get())."""
    counts: dict[str, int] = {}
    counts[key] += 1
    return counts[key]

def typo_variable_demo(position: int) -> int:
    """Typo in local variable name (auto-patchable: Levenshtein match)."""
    total_score: int = position * 10
    return totl_score + 1

def attribute_problem(value: Any) -> str:
    """AttributeError on int without upper() (auto-patchable: str(value).upper())."""
    return value.upper()

def string_concat_demo(data: list[int]) -> str:
    """TypeError concatenating int + str (auto-patchable: str())."""
    return len(data) + " items recorded"

def len_number_demo(number: int) -> int:
    """TypeError calling len() on int (auto-patchable: len(str()))."""
    return len(number)

def literal_alias_demo() -> bool:
    """NameError lowercase true (auto-patchable: True)."""
    return true

def run_demo() -> None:
    print("File 1: deliberate-error demonstration")
    actions = [
        lambda: safe_divide(10, 0),
        lambda: parse_word_number("forty-two"),
        lambda: counter_pattern_demo("hits"),
        lambda: typo_variable_demo(5),
        lambda: attribute_problem(42),
        lambda: string_concat_demo([1, 2, 3]),
        lambda: len_number_demo(12345),
        lambda: literal_alias_demo(),
    ]
    for action in actions:
        try:
            print(action())
        except Exception as error:
            print(type(error).__name__, error)

if __name__ == "__main__":
    run_demo()

# The generated cases below provide a large set of independent test targets (500+ lines).
# Balanced between patchable idiomatic fixes and explain-only manual fixes.

def test_case_001(data: list[int], position: int = 1) -> int:
    """Generated test case 001: patchable variable typo."""
    total_accum_1: int = position * 10
    return totl_accum_1 + 1  # NameError: typo of total_accum_1 -> auto-patched


def test_case_002(data: list[int], position: int = 2) -> str:
    """Generated test case 002: patchable str + int concat."""
    return len(data) + " items recorded"  # TypeError: int + str -> auto-patched


def test_case_003(data: list[int], position: int = 3) -> int:
    """Generated test case 003: patchable number word."""
    return int("forty-two")  # ValueError: number word -> auto-patched to int(42)


def test_case_004(data: list[int], position: int = 4) -> int:
    """Generated test case 004: patchable dict counter."""
    counts_4: dict[str, int] = {}
    counts_4["hits"] += position  # KeyError: counter idiom -> auto-patched with .get()
    return counts_4["hits"]


def test_case_005(data: list[int], position: int = 5) -> str:
    """Generated test case 005: patchable attribute error."""
    return position.upper()  # AttributeError: int.upper() -> auto-patched to str().upper()


def test_case_006(data: list[int], position: int = 6) -> int:
    """Generated test case 006: patchable len() on int."""
    return len(position)  # TypeError: len(int) -> auto-patched to len(str())


def test_case_007(data: list[int], position: int = 7) -> bool:
    """Generated test case 007: patchable literal alias."""
    return true  # NameError: lowercase true -> auto-patched to True


def test_case_008(data: list[int], position: int = 8) -> int:
    """Generated test case 008: unfixable division by zero."""
    return 8 // 0  # ZeroDivisionError: manual fix required


def test_case_009(data: list[int], position: int = 9) -> int:
    """Generated test case 009: unfixable index error."""
    items_9 = [1, 2, 3]
    return items_9[99]  # IndexError: manual fix required


def test_case_010(data: list[int], position: int = 10) -> str:
    """Generated test case 010: unfixable missing key."""
    user_10 = {"id": 10}
    return user_10["name"]  # KeyError: manual fix required


def test_case_011(data: list[int], position: int = 11) -> int:
    """Generated test case 011: patchable variable typo."""
    total_accum_11: int = position * 10
    return totl_accum_11 + 1  # NameError: typo of total_accum_11 -> auto-patched


def test_case_012(data: list[int], position: int = 12) -> str:
    """Generated test case 012: patchable str + int concat."""
    return len(data) + " items recorded"  # TypeError: int + str -> auto-patched


def test_case_013(data: list[int], position: int = 13) -> int:
    """Generated test case 013: patchable number word."""
    return int("forty-two")  # ValueError: number word -> auto-patched to int(42)


def test_case_014(data: list[int], position: int = 14) -> int:
    """Generated test case 014: patchable dict counter."""
    counts_14: dict[str, int] = {}
    counts_14["hits"] += position  # KeyError: counter idiom -> auto-patched with .get()
    return counts_14["hits"]


def test_case_015(data: list[int], position: int = 15) -> str:
    """Generated test case 015: patchable attribute error."""
    return position.upper()  # AttributeError: int.upper() -> auto-patched to str().upper()


def test_case_016(data: list[int], position: int = 16) -> int:
    """Generated test case 016: patchable len() on int."""
    return len(position)  # TypeError: len(int) -> auto-patched to len(str())


def test_case_017(data: list[int], position: int = 17) -> bool:
    """Generated test case 017: patchable literal alias."""
    return true  # NameError: lowercase true -> auto-patched to True


def test_case_018(data: list[int], position: int = 18) -> int:
    """Generated test case 018: unfixable division by zero."""
    return 18 // 0  # ZeroDivisionError: manual fix required


def test_case_019(data: list[int], position: int = 19) -> int:
    """Generated test case 019: unfixable index error."""
    items_19 = [1, 2, 3]
    return items_19[99]  # IndexError: manual fix required


def test_case_020(data: list[int], position: int = 20) -> str:
    """Generated test case 020: unfixable missing key."""
    user_20 = {"id": 20}
    return user_20["name"]  # KeyError: manual fix required


def test_case_021(data: list[int], position: int = 21) -> int:
    """Generated test case 021: patchable variable typo."""
    total_accum_21: int = position * 10
    return totl_accum_21 + 1  # NameError: typo of total_accum_21 -> auto-patched


def test_case_022(data: list[int], position: int = 22) -> str:
    """Generated test case 022: patchable str + int concat."""
    return len(data) + " items recorded"  # TypeError: int + str -> auto-patched


def test_case_023(data: list[int], position: int = 23) -> int:
    """Generated test case 023: patchable number word."""
    return int("forty-two")  # ValueError: number word -> auto-patched to int(42)


def test_case_024(data: list[int], position: int = 24) -> int:
    """Generated test case 024: patchable dict counter."""
    counts_24: dict[str, int] = {}
    counts_24["hits"] += position  # KeyError: counter idiom -> auto-patched with .get()
    return counts_24["hits"]


def test_case_025(data: list[int], position: int = 25) -> str:
    """Generated test case 025: patchable attribute error."""
    return position.upper()  # AttributeError: int.upper() -> auto-patched to str().upper()


def test_case_026(data: list[int], position: int = 26) -> int:
    """Generated test case 026: patchable len() on int."""
    return len(position)  # TypeError: len(int) -> auto-patched to len(str())


def test_case_027(data: list[int], position: int = 27) -> bool:
    """Generated test case 027: patchable literal alias."""
    return true  # NameError: lowercase true -> auto-patched to True


def test_case_028(data: list[int], position: int = 28) -> int:
    """Generated test case 028: unfixable division by zero."""
    return 28 // 0  # ZeroDivisionError: manual fix required


def test_case_029(data: list[int], position: int = 29) -> int:
    """Generated test case 029: unfixable index error."""
    items_29 = [1, 2, 3]
    return items_29[99]  # IndexError: manual fix required


def test_case_030(data: list[int], position: int = 30) -> str:
    """Generated test case 030: unfixable missing key."""
    user_30 = {"id": 30}
    return user_30["name"]  # KeyError: manual fix required


def test_case_031(data: list[int], position: int = 31) -> int:
    """Generated test case 031: patchable variable typo."""
    total_accum_31: int = position * 10
    return totl_accum_31 + 1  # NameError: typo of total_accum_31 -> auto-patched


def test_case_032(data: list[int], position: int = 32) -> str:
    """Generated test case 032: patchable str + int concat."""
    return len(data) + " items recorded"  # TypeError: int + str -> auto-patched


def test_case_033(data: list[int], position: int = 33) -> int:
    """Generated test case 033: patchable number word."""
    return int("forty-two")  # ValueError: number word -> auto-patched to int(42)


def test_case_034(data: list[int], position: int = 34) -> int:
    """Generated test case 034: patchable dict counter."""
    counts_34: dict[str, int] = {}
    counts_34["hits"] += position  # KeyError: counter idiom -> auto-patched with .get()
    return counts_34["hits"]


def test_case_035(data: list[int], position: int = 35) -> str:
    """Generated test case 035: patchable attribute error."""
    return position.upper()  # AttributeError: int.upper() -> auto-patched to str().upper()


def test_case_036(data: list[int], position: int = 36) -> int:
    """Generated test case 036: patchable len() on int."""
    return len(position)  # TypeError: len(int) -> auto-patched to len(str())


def test_case_037(data: list[int], position: int = 37) -> bool:
    """Generated test case 037: patchable literal alias."""
    return true  # NameError: lowercase true -> auto-patched to True


def test_case_038(data: list[int], position: int = 38) -> int:
    """Generated test case 038: unfixable division by zero."""
    return 38 // 0  # ZeroDivisionError: manual fix required


def test_case_039(data: list[int], position: int = 39) -> int:
    """Generated test case 039: unfixable index error."""
    items_39 = [1, 2, 3]
    return items_39[99]  # IndexError: manual fix required


def test_case_040(data: list[int], position: int = 40) -> str:
    """Generated test case 040: unfixable missing key."""
    user_40 = {"id": 40}
    return user_40["name"]  # KeyError: manual fix required


def test_case_041(data: list[int], position: int = 41) -> int:
    """Generated test case 041: patchable variable typo."""
    total_accum_41: int = position * 10
    return totl_accum_41 + 1  # NameError: typo of total_accum_41 -> auto-patched


def test_case_042(data: list[int], position: int = 42) -> str:
    """Generated test case 042: patchable str + int concat."""
    return len(data) + " items recorded"  # TypeError: int + str -> auto-patched


def test_case_043(data: list[int], position: int = 43) -> int:
    """Generated test case 043: patchable number word."""
    return int("forty-two")  # ValueError: number word -> auto-patched to int(42)


def test_case_044(data: list[int], position: int = 44) -> int:
    """Generated test case 044: patchable dict counter."""
    counts_44: dict[str, int] = {}
    counts_44["hits"] += position  # KeyError: counter idiom -> auto-patched with .get()
    return counts_44["hits"]


def test_case_045(data: list[int], position: int = 45) -> str:
    """Generated test case 045: patchable attribute error."""
    return position.upper()  # AttributeError: int.upper() -> auto-patched to str().upper()


def test_case_046(data: list[int], position: int = 46) -> int:
    """Generated test case 046: patchable len() on int."""
    return len(position)  # TypeError: len(int) -> auto-patched to len(str())


def test_case_047(data: list[int], position: int = 47) -> bool:
    """Generated test case 047: patchable literal alias."""
    return true  # NameError: lowercase true -> auto-patched to True


def test_case_048(data: list[int], position: int = 48) -> int:
    """Generated test case 048: unfixable division by zero."""
    return 48 // 0  # ZeroDivisionError: manual fix required


def test_case_049(data: list[int], position: int = 49) -> int:
    """Generated test case 049: unfixable index error."""
    items_49 = [1, 2, 3]
    return items_49[99]  # IndexError: manual fix required


def test_case_050(data: list[int], position: int = 50) -> str:
    """Generated test case 050: unfixable missing key."""
    user_50 = {"id": 50}
    return user_50["name"]  # KeyError: manual fix required


def test_case_051(data: list[int], position: int = 51) -> int:
    """Generated test case 051: patchable variable typo."""
    total_accum_51: int = position * 10
    return totl_accum_51 + 1  # NameError: typo of total_accum_51 -> auto-patched


def test_case_052(data: list[int], position: int = 52) -> str:
    """Generated test case 052: patchable str + int concat."""
    return len(data) + " items recorded"  # TypeError: int + str -> auto-patched


def test_case_053(data: list[int], position: int = 53) -> int:
    """Generated test case 053: patchable number word."""
    return int("forty-two")  # ValueError: number word -> auto-patched to int(42)


def test_case_054(data: list[int], position: int = 54) -> int:
    """Generated test case 054: patchable dict counter."""
    counts_54: dict[str, int] = {}
    counts_54["hits"] += position  # KeyError: counter idiom -> auto-patched with .get()
    return counts_54["hits"]


def test_case_055(data: list[int], position: int = 55) -> str:
    """Generated test case 055: patchable attribute error."""
    return position.upper()  # AttributeError: int.upper() -> auto-patched to str().upper()


def test_case_056(data: list[int], position: int = 56) -> int:
    """Generated test case 056: patchable len() on int."""
    return len(position)  # TypeError: len(int) -> auto-patched to len(str())


def test_case_057(data: list[int], position: int = 57) -> bool:
    """Generated test case 057: patchable literal alias."""
    return true  # NameError: lowercase true -> auto-patched to True


def test_case_058(data: list[int], position: int = 58) -> int:
    """Generated test case 058: unfixable division by zero."""
    return 58 // 0  # ZeroDivisionError: manual fix required


def test_case_059(data: list[int], position: int = 59) -> int:
    """Generated test case 059: unfixable index error."""
    items_59 = [1, 2, 3]
    return items_59[99]  # IndexError: manual fix required


def test_case_060(data: list[int], position: int = 60) -> str:
    """Generated test case 060: unfixable missing key."""
    user_60 = {"id": 60}
    return user_60["name"]  # KeyError: manual fix required


def test_case_061(data: list[int], position: int = 61) -> int:
    """Generated test case 061: patchable variable typo."""
    total_accum_61: int = position * 10
    return totl_accum_61 + 1  # NameError: typo of total_accum_61 -> auto-patched


def test_case_062(data: list[int], position: int = 62) -> str:
    """Generated test case 062: patchable str + int concat."""
    return len(data) + " items recorded"  # TypeError: int + str -> auto-patched


def test_case_063(data: list[int], position: int = 63) -> int:
    """Generated test case 063: patchable number word."""
    return int("forty-two")  # ValueError: number word -> auto-patched to int(42)


def test_case_064(data: list[int], position: int = 64) -> int:
    """Generated test case 064: patchable dict counter."""
    counts_64: dict[str, int] = {}
    counts_64["hits"] += position  # KeyError: counter idiom -> auto-patched with .get()
    return counts_64["hits"]


def test_case_065(data: list[int], position: int = 65) -> str:
    """Generated test case 065: patchable attribute error."""
    return position.upper()  # AttributeError: int.upper() -> auto-patched to str().upper()


def test_case_066(data: list[int], position: int = 66) -> int:
    """Generated test case 066: patchable len() on int."""
    return len(position)  # TypeError: len(int) -> auto-patched to len(str())


def test_case_067(data: list[int], position: int = 67) -> bool:
    """Generated test case 067: patchable literal alias."""
    return true  # NameError: lowercase true -> auto-patched to True


def test_case_068(data: list[int], position: int = 68) -> int:
    """Generated test case 068: unfixable division by zero."""
    return 68 // 0  # ZeroDivisionError: manual fix required


def test_case_069(data: list[int], position: int = 69) -> int:
    """Generated test case 069: unfixable index error."""
    items_69 = [1, 2, 3]
    return items_69[99]  # IndexError: manual fix required


def test_case_070(data: list[int], position: int = 70) -> str:
    """Generated test case 070: unfixable missing key."""
    user_70 = {"id": 70}
    return user_70["name"]  # KeyError: manual fix required


def test_case_071(data: list[int], position: int = 71) -> int:
    """Generated test case 071: patchable variable typo."""
    total_accum_71: int = position * 10
    return totl_accum_71 + 1  # NameError: typo of total_accum_71 -> auto-patched


def test_case_072(data: list[int], position: int = 72) -> str:
    """Generated test case 072: patchable str + int concat."""
    return len(data) + " items recorded"  # TypeError: int + str -> auto-patched


def test_case_073(data: list[int], position: int = 73) -> int:
    """Generated test case 073: patchable number word."""
    return int("forty-two")  # ValueError: number word -> auto-patched to int(42)


def test_case_074(data: list[int], position: int = 74) -> int:
    """Generated test case 074: patchable dict counter."""
    counts_74: dict[str, int] = {}
    counts_74["hits"] += position  # KeyError: counter idiom -> auto-patched with .get()
    return counts_74["hits"]


def test_case_075(data: list[int], position: int = 75) -> str:
    """Generated test case 075: patchable attribute error."""
    return position.upper()  # AttributeError: int.upper() -> auto-patched to str().upper()


def test_case_076(data: list[int], position: int = 76) -> int:
    """Generated test case 076: patchable len() on int."""
    return len(position)  # TypeError: len(int) -> auto-patched to len(str())


def test_case_077(data: list[int], position: int = 77) -> bool:
    """Generated test case 077: patchable literal alias."""
    return true  # NameError: lowercase true -> auto-patched to True


def test_case_078(data: list[int], position: int = 78) -> int:
    """Generated test case 078: unfixable division by zero."""
    return 78 // 0  # ZeroDivisionError: manual fix required


def test_case_079(data: list[int], position: int = 79) -> int:
    """Generated test case 079: unfixable index error."""
    items_79 = [1, 2, 3]
    return items_79[99]  # IndexError: manual fix required


def test_case_080(data: list[int], position: int = 80) -> str:
    """Generated test case 080: unfixable missing key."""
    user_80 = {"id": 80}
    return user_80["name"]  # KeyError: manual fix required


def test_case_081(data: list[int], position: int = 81) -> int:
    """Generated test case 081: patchable variable typo."""
    total_accum_81: int = position * 10
    return totl_accum_81 + 1  # NameError: typo of total_accum_81 -> auto-patched


def test_case_082(data: list[int], position: int = 82) -> str:
    """Generated test case 082: patchable str + int concat."""
    return len(data) + " items recorded"  # TypeError: int + str -> auto-patched


def test_case_083(data: list[int], position: int = 83) -> int:
    """Generated test case 083: patchable number word."""
    return int("forty-two")  # ValueError: number word -> auto-patched to int(42)


def test_case_084(data: list[int], position: int = 84) -> int:
    """Generated test case 084: patchable dict counter."""
    counts_84: dict[str, int] = {}
    counts_84["hits"] += position  # KeyError: counter idiom -> auto-patched with .get()
    return counts_84["hits"]


def test_case_085(data: list[int], position: int = 85) -> str:
    """Generated test case 085: patchable attribute error."""
    return position.upper()  # AttributeError: int.upper() -> auto-patched to str().upper()


def test_case_086(data: list[int], position: int = 86) -> int:
    """Generated test case 086: patchable len() on int."""
    return len(position)  # TypeError: len(int) -> auto-patched to len(str())


def test_case_087(data: list[int], position: int = 87) -> bool:
    """Generated test case 087: patchable literal alias."""
    return true  # NameError: lowercase true -> auto-patched to True


def test_case_088(data: list[int], position: int = 88) -> int:
    """Generated test case 088: unfixable division by zero."""
    return 88 // 0  # ZeroDivisionError: manual fix required


def test_case_089(data: list[int], position: int = 89) -> int:
    """Generated test case 089: unfixable index error."""
    items_89 = [1, 2, 3]
    return items_89[99]  # IndexError: manual fix required


def test_case_090(data: list[int], position: int = 90) -> str:
    """Generated test case 090: unfixable missing key."""
    user_90 = {"id": 90}
    return user_90["name"]  # KeyError: manual fix required


def test_case_091(data: list[int], position: int = 91) -> int:
    """Generated test case 091: patchable variable typo."""
    total_accum_91: int = position * 10
    return totl_accum_91 + 1  # NameError: typo of total_accum_91 -> auto-patched


def test_case_092(data: list[int], position: int = 92) -> str:
    """Generated test case 092: patchable str + int concat."""
    return len(data) + " items recorded"  # TypeError: int + str -> auto-patched


def test_case_093(data: list[int], position: int = 93) -> int:
    """Generated test case 093: patchable number word."""
    return int("forty-two")  # ValueError: number word -> auto-patched to int(42)


def test_case_094(data: list[int], position: int = 94) -> int:
    """Generated test case 094: patchable dict counter."""
    counts_94: dict[str, int] = {}
    counts_94["hits"] += position  # KeyError: counter idiom -> auto-patched with .get()
    return counts_94["hits"]


def test_case_095(data: list[int], position: int = 95) -> str:
    """Generated test case 095: patchable attribute error."""
    return position.upper()  # AttributeError: int.upper() -> auto-patched to str().upper()


def test_case_096(data: list[int], position: int = 96) -> int:
    """Generated test case 096: patchable len() on int."""
    return len(position)  # TypeError: len(int) -> auto-patched to len(str())


def test_case_097(data: list[int], position: int = 97) -> bool:
    """Generated test case 097: patchable literal alias."""
    return true  # NameError: lowercase true -> auto-patched to True


def test_case_098(data: list[int], position: int = 98) -> int:
    """Generated test case 098: unfixable division by zero."""
    return 98 // 0  # ZeroDivisionError: manual fix required


def test_case_099(data: list[int], position: int = 99) -> int:
    """Generated test case 099: unfixable index error."""
    items_99 = [1, 2, 3]
    return items_99[99]  # IndexError: manual fix required


def test_case_100(data: list[int], position: int = 100) -> str:
    """Generated test case 100: unfixable missing key."""
    user_100 = {"id": 100}
    return user_100["name"]  # KeyError: manual fix required


def test_case_101(data: list[int], position: int = 101) -> int:
    """Generated test case 101: patchable variable typo."""
    total_accum_101: int = position * 10
    return totl_accum_101 + 1  # NameError: typo of total_accum_101 -> auto-patched


def test_case_102(data: list[int], position: int = 102) -> str:
    """Generated test case 102: patchable str + int concat."""
    return len(data) + " items recorded"  # TypeError: int + str -> auto-patched


def test_case_103(data: list[int], position: int = 103) -> int:
    """Generated test case 103: patchable number word."""
    return int("forty-two")  # ValueError: number word -> auto-patched to int(42)


def test_case_104(data: list[int], position: int = 104) -> int:
    """Generated test case 104: patchable dict counter."""
    counts_104: dict[str, int] = {}
    counts_104["hits"] += position  # KeyError: counter idiom -> auto-patched with .get()
    return counts_104["hits"]


def test_case_105(data: list[int], position: int = 105) -> str:
    """Generated test case 105: patchable attribute error."""
    return position.upper()  # AttributeError: int.upper() -> auto-patched to str().upper()
