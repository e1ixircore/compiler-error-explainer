"""
INTENTIONALLY BUGGY TEST FILE 1
Purpose: exercise static analyzers and runtime error detection.
This file contains deliberate defects. Do not use in production.
Run with: python buggy_test_file_1.py
Static checks: try pyright, mypy, ruff, or pylint.
"""
from __future__ import annotations
import math
import json
from pathlib import Path
from typing import Any

def safe_divide(a: float, b: float) -> float:
    """Deliberate runtime division-by-zero possibility."""
    return a / b

def get_item(values: list[int], index: int) -> int:
    """Deliberate runtime index error possibility."""
    return values[index]

def parse_number(value: str) -> int:
    """Deliberate runtime conversion error possibility."""
    return int(value)

def get_user_name(user: dict[str, Any]) -> str:
    """Deliberate runtime missing-key possibility."""
    return user["name"]

def calculate_average(values: list[float]) -> float:
    """Deliberate empty-list division error."""
    return sum(values) / len(values)

def static_type_problem() -> int:
    # Static-analysis defect: returns a string despite int annotation.
    return "not an integer"

def undefined_name_problem() -> int:
    # Static-analysis defect: undefined name.
    return missing_total + 1

def attribute_problem(value: Any) -> str:
    # Runtime AttributeError for values without upper().
    return value.upper()

def logical_problem(number: int) -> bool:
    # Logical defect: this condition is almost certainly inverted.
    return number < 0

def run_demo() -> None:
    print("File 1: deliberate-error demonstration")
    actions = [
        lambda: safe_divide(10, 0),
        lambda: get_item([1, 2, 3], 9),
        lambda: parse_number("abc"),
        lambda: get_user_name({"id": 7}),
        lambda: calculate_average([]),
        lambda: attribute_problem(42),
    ]
    for action in actions:
        try:
            print(action())
        except Exception as error:
            print(type(error).__name__, error)

if __name__ == "__main__":
    run_demo()

# The generated cases below provide a large set of independent test targets.
# Many contain deliberate static or runtime defects.

def test_case_001(data: list[int], position: int = 1) -> int:
    """Generated test case 001; defect class 1."""
    return data[101]  # runtime IndexError for short lists


def test_case_002(data: list[int], position: int = 2) -> int:
    """Generated test case 002; defect class 2."""
    return 2 // (position - 2)  # ZeroDivisionError at default


def test_case_003(data: list[int], position: int = 3) -> int:
    """Generated test case 003; defect class 3."""
    return absent_value_3  # undefined name: static-analysis failure


def test_case_004(data: list[int], position: int = 4) -> int:
    """Generated test case 004; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_005(data: list[int], position: int = 0) -> int:
    """Generated test case 005; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 5

def test_case_006(data: list[int], position: int = 1) -> int:
    """Generated test case 006; defect class 6."""
    return int("bad_6")  # runtime ValueError


def test_case_007(data: list[int], position: int = 2) -> int:
    """Generated test case 007; defect class 0."""
    result: int = "case_007"  # static type mismatch
    return result

def test_case_008(data: list[int], position: int = 3) -> int:
    """Generated test case 008; defect class 1."""
    return data[108]  # runtime IndexError for short lists


def test_case_009(data: list[int], position: int = 4) -> int:
    """Generated test case 009; defect class 2."""
    return 9 // (position - 4)  # ZeroDivisionError at default


def test_case_010(data: list[int], position: int = 0) -> int:
    """Generated test case 010; defect class 3."""
    return absent_value_10  # undefined name: static-analysis failure


def test_case_011(data: list[int], position: int = 1) -> int:
    """Generated test case 011; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_012(data: list[int], position: int = 2) -> int:
    """Generated test case 012; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 12

def test_case_013(data: list[int], position: int = 3) -> int:
    """Generated test case 013; defect class 6."""
    return int("bad_13")  # runtime ValueError


def test_case_014(data: list[int], position: int = 4) -> int:
    """Generated test case 014; defect class 0."""
    result: int = "case_014"  # static type mismatch
    return result

def test_case_015(data: list[int], position: int = 0) -> int:
    """Generated test case 015; defect class 1."""
    return data[115]  # runtime IndexError for short lists


def test_case_016(data: list[int], position: int = 1) -> int:
    """Generated test case 016; defect class 2."""
    return 16 // (position - 1)  # ZeroDivisionError at default


def test_case_017(data: list[int], position: int = 2) -> int:
    """Generated test case 017; defect class 3."""
    return absent_value_17  # undefined name: static-analysis failure


def test_case_018(data: list[int], position: int = 3) -> int:
    """Generated test case 018; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_019(data: list[int], position: int = 4) -> int:
    """Generated test case 019; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 19

def test_case_020(data: list[int], position: int = 0) -> int:
    """Generated test case 020; defect class 6."""
    return int("bad_20")  # runtime ValueError


def test_case_021(data: list[int], position: int = 1) -> int:
    """Generated test case 021; defect class 0."""
    result: int = "case_021"  # static type mismatch
    return result

def test_case_022(data: list[int], position: int = 2) -> int:
    """Generated test case 022; defect class 1."""
    return data[122]  # runtime IndexError for short lists


def test_case_023(data: list[int], position: int = 3) -> int:
    """Generated test case 023; defect class 2."""
    return 23 // (position - 3)  # ZeroDivisionError at default


def test_case_024(data: list[int], position: int = 4) -> int:
    """Generated test case 024; defect class 3."""
    return absent_value_24  # undefined name: static-analysis failure


def test_case_025(data: list[int], position: int = 0) -> int:
    """Generated test case 025; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_026(data: list[int], position: int = 1) -> int:
    """Generated test case 026; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 26

def test_case_027(data: list[int], position: int = 2) -> int:
    """Generated test case 027; defect class 6."""
    return int("bad_27")  # runtime ValueError


def test_case_028(data: list[int], position: int = 3) -> int:
    """Generated test case 028; defect class 0."""
    result: int = "case_028"  # static type mismatch
    return result

def test_case_029(data: list[int], position: int = 4) -> int:
    """Generated test case 029; defect class 1."""
    return data[129]  # runtime IndexError for short lists


def test_case_030(data: list[int], position: int = 0) -> int:
    """Generated test case 030; defect class 2."""
    return 30 // (position - 0)  # ZeroDivisionError at default


def test_case_031(data: list[int], position: int = 1) -> int:
    """Generated test case 031; defect class 3."""
    return absent_value_31  # undefined name: static-analysis failure


def test_case_032(data: list[int], position: int = 2) -> int:
    """Generated test case 032; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_033(data: list[int], position: int = 3) -> int:
    """Generated test case 033; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 33

def test_case_034(data: list[int], position: int = 4) -> int:
    """Generated test case 034; defect class 6."""
    return int("bad_34")  # runtime ValueError


def test_case_035(data: list[int], position: int = 0) -> int:
    """Generated test case 035; defect class 0."""
    result: int = "case_035"  # static type mismatch
    return result

def test_case_036(data: list[int], position: int = 1) -> int:
    """Generated test case 036; defect class 1."""
    return data[136]  # runtime IndexError for short lists


def test_case_037(data: list[int], position: int = 2) -> int:
    """Generated test case 037; defect class 2."""
    return 37 // (position - 2)  # ZeroDivisionError at default


def test_case_038(data: list[int], position: int = 3) -> int:
    """Generated test case 038; defect class 3."""
    return absent_value_38  # undefined name: static-analysis failure


def test_case_039(data: list[int], position: int = 4) -> int:
    """Generated test case 039; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_040(data: list[int], position: int = 0) -> int:
    """Generated test case 040; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 40

def test_case_041(data: list[int], position: int = 1) -> int:
    """Generated test case 041; defect class 6."""
    return int("bad_41")  # runtime ValueError


def test_case_042(data: list[int], position: int = 2) -> int:
    """Generated test case 042; defect class 0."""
    result: int = "case_042"  # static type mismatch
    return result

def test_case_043(data: list[int], position: int = 3) -> int:
    """Generated test case 043; defect class 1."""
    return data[143]  # runtime IndexError for short lists


def test_case_044(data: list[int], position: int = 4) -> int:
    """Generated test case 044; defect class 2."""
    return 44 // (position - 4)  # ZeroDivisionError at default


def test_case_045(data: list[int], position: int = 0) -> int:
    """Generated test case 045; defect class 3."""
    return absent_value_45  # undefined name: static-analysis failure


def test_case_046(data: list[int], position: int = 1) -> int:
    """Generated test case 046; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_047(data: list[int], position: int = 2) -> int:
    """Generated test case 047; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 47

def test_case_048(data: list[int], position: int = 3) -> int:
    """Generated test case 048; defect class 6."""
    return int("bad_48")  # runtime ValueError


def test_case_049(data: list[int], position: int = 4) -> int:
    """Generated test case 049; defect class 0."""
    result: int = "case_049"  # static type mismatch
    return result

def test_case_050(data: list[int], position: int = 0) -> int:
    """Generated test case 050; defect class 1."""
    return data[150]  # runtime IndexError for short lists


def test_case_051(data: list[int], position: int = 1) -> int:
    """Generated test case 051; defect class 2."""
    return 51 // (position - 1)  # ZeroDivisionError at default


def test_case_052(data: list[int], position: int = 2) -> int:
    """Generated test case 052; defect class 3."""
    return absent_value_52  # undefined name: static-analysis failure


def test_case_053(data: list[int], position: int = 3) -> int:
    """Generated test case 053; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_054(data: list[int], position: int = 4) -> int:
    """Generated test case 054; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 54

def test_case_055(data: list[int], position: int = 0) -> int:
    """Generated test case 055; defect class 6."""
    return int("bad_55")  # runtime ValueError


def test_case_056(data: list[int], position: int = 1) -> int:
    """Generated test case 056; defect class 0."""
    result: int = "case_056"  # static type mismatch
    return result

def test_case_057(data: list[int], position: int = 2) -> int:
    """Generated test case 057; defect class 1."""
    return data[157]  # runtime IndexError for short lists


def test_case_058(data: list[int], position: int = 3) -> int:
    """Generated test case 058; defect class 2."""
    return 58 // (position - 3)  # ZeroDivisionError at default


def test_case_059(data: list[int], position: int = 4) -> int:
    """Generated test case 059; defect class 3."""
    return absent_value_59  # undefined name: static-analysis failure


def test_case_060(data: list[int], position: int = 0) -> int:
    """Generated test case 060; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_061(data: list[int], position: int = 1) -> int:
    """Generated test case 061; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 61

def test_case_062(data: list[int], position: int = 2) -> int:
    """Generated test case 062; defect class 6."""
    return int("bad_62")  # runtime ValueError


def test_case_063(data: list[int], position: int = 3) -> int:
    """Generated test case 063; defect class 0."""
    result: int = "case_063"  # static type mismatch
    return result

def test_case_064(data: list[int], position: int = 4) -> int:
    """Generated test case 064; defect class 1."""
    return data[164]  # runtime IndexError for short lists


def test_case_065(data: list[int], position: int = 0) -> int:
    """Generated test case 065; defect class 2."""
    return 65 // (position - 0)  # ZeroDivisionError at default


def test_case_066(data: list[int], position: int = 1) -> int:
    """Generated test case 066; defect class 3."""
    return absent_value_66  # undefined name: static-analysis failure


def test_case_067(data: list[int], position: int = 2) -> int:
    """Generated test case 067; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_068(data: list[int], position: int = 3) -> int:
    """Generated test case 068; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 68

def test_case_069(data: list[int], position: int = 4) -> int:
    """Generated test case 069; defect class 6."""
    return int("bad_69")  # runtime ValueError


def test_case_070(data: list[int], position: int = 0) -> int:
    """Generated test case 070; defect class 0."""
    result: int = "case_070"  # static type mismatch
    return result

def test_case_071(data: list[int], position: int = 1) -> int:
    """Generated test case 071; defect class 1."""
    return data[171]  # runtime IndexError for short lists


def test_case_072(data: list[int], position: int = 2) -> int:
    """Generated test case 072; defect class 2."""
    return 72 // (position - 2)  # ZeroDivisionError at default


def test_case_073(data: list[int], position: int = 3) -> int:
    """Generated test case 073; defect class 3."""
    return absent_value_73  # undefined name: static-analysis failure


def test_case_074(data: list[int], position: int = 4) -> int:
    """Generated test case 074; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_075(data: list[int], position: int = 0) -> int:
    """Generated test case 075; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 75

def test_case_076(data: list[int], position: int = 1) -> int:
    """Generated test case 076; defect class 6."""
    return int("bad_76")  # runtime ValueError


def test_case_077(data: list[int], position: int = 2) -> int:
    """Generated test case 077; defect class 0."""
    result: int = "case_077"  # static type mismatch
    return result

def test_case_078(data: list[int], position: int = 3) -> int:
    """Generated test case 078; defect class 1."""
    return data[178]  # runtime IndexError for short lists


def test_case_079(data: list[int], position: int = 4) -> int:
    """Generated test case 079; defect class 2."""
    return 79 // (position - 4)  # ZeroDivisionError at default


def test_case_080(data: list[int], position: int = 0) -> int:
    """Generated test case 080; defect class 3."""
    return absent_value_80  # undefined name: static-analysis failure


def test_case_081(data: list[int], position: int = 1) -> int:
    """Generated test case 081; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_082(data: list[int], position: int = 2) -> int:
    """Generated test case 082; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 82

def test_case_083(data: list[int], position: int = 3) -> int:
    """Generated test case 083; defect class 6."""
    return int("bad_83")  # runtime ValueError


def test_case_084(data: list[int], position: int = 4) -> int:
    """Generated test case 084; defect class 0."""
    result: int = "case_084"  # static type mismatch
    return result

def test_case_085(data: list[int], position: int = 0) -> int:
    """Generated test case 085; defect class 1."""
    return data[185]  # runtime IndexError for short lists


def test_case_086(data: list[int], position: int = 1) -> int:
    """Generated test case 086; defect class 2."""
    return 86 // (position - 1)  # ZeroDivisionError at default


def test_case_087(data: list[int], position: int = 2) -> int:
    """Generated test case 087; defect class 3."""
    return absent_value_87  # undefined name: static-analysis failure


def test_case_088(data: list[int], position: int = 3) -> int:
    """Generated test case 088; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_089(data: list[int], position: int = 4) -> int:
    """Generated test case 089; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 89

def test_case_090(data: list[int], position: int = 0) -> int:
    """Generated test case 090; defect class 6."""
    return int("bad_90")  # runtime ValueError


def test_case_091(data: list[int], position: int = 1) -> int:
    """Generated test case 091; defect class 0."""
    result: int = "case_091"  # static type mismatch
    return result

def test_case_092(data: list[int], position: int = 2) -> int:
    """Generated test case 092; defect class 1."""
    return data[192]  # runtime IndexError for short lists


def test_case_093(data: list[int], position: int = 3) -> int:
    """Generated test case 093; defect class 2."""
    return 93 // (position - 3)  # ZeroDivisionError at default


def test_case_094(data: list[int], position: int = 4) -> int:
    """Generated test case 094; defect class 3."""
    return absent_value_94  # undefined name: static-analysis failure


def test_case_095(data: list[int], position: int = 0) -> int:
    """Generated test case 095; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_096(data: list[int], position: int = 1) -> int:
    """Generated test case 096; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 96

def test_case_097(data: list[int], position: int = 2) -> int:
    """Generated test case 097; defect class 6."""
    return int("bad_97")  # runtime ValueError


def test_case_098(data: list[int], position: int = 3) -> int:
    """Generated test case 098; defect class 0."""
    result: int = "case_098"  # static type mismatch
    return result

def test_case_099(data: list[int], position: int = 4) -> int:
    """Generated test case 099; defect class 1."""
    return data[199]  # runtime IndexError for short lists


def test_case_100(data: list[int], position: int = 0) -> int:
    """Generated test case 100; defect class 2."""
    return 100 // (position - 0)  # ZeroDivisionError at default


def test_case_101(data: list[int], position: int = 1) -> int:
    """Generated test case 101; defect class 3."""
    return absent_value_101  # undefined name: static-analysis failure


def test_case_102(data: list[int], position: int = 2) -> int:
    """Generated test case 102; defect class 4."""
    return len(data) + "items"  # static type mismatch


def test_case_103(data: list[int], position: int = 3) -> int:
    """Generated test case 103; defect class 5."""
    if position > len(data):
        return data[position]  # off-by-one boundary defect
    return 103

def test_case_104(data: list[int], position: int = 4) -> int:
    """Generated test case 104; defect class 6."""
    return int("bad_104")  # runtime ValueError


def test_case_105(data: list[int], position: int = 0) -> int:
    """Generated test case 105; defect class 0."""
    result: int = "case_105"  # static type mismatch
    return result

