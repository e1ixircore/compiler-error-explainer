// test_cpp_basics.cpp - 550+ lines with common beginner C++ mistakes
// Deliberate defects: missing <iostream>, missing std:: prefix (cout/endl), missing semicolon, variable typo.

// Clean C++ utility functions (no defects, no warnings).

int add_numbers(int a, int b) {
    return a + b;
}

double multiply_numbers(double a, double b) {
    return a * b;
}

bool is_even(int value) {
    return value % 2 == 0;
}

int clamp_value(int value, int low, int high) {
    if (value < low) return low;
    if (value > high) return high;
    return value;
}

double safe_divide(double a, double b) {
    if (b == 0.0) return 0.0;
    return a / b;
}

int basics_utility_001(int value, int offset = 1) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_002(int value, int offset = 2) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_003(int value, int offset = 3) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_004(int value, int offset = 4) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_005(int value, int offset = 5) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_006(int value, int offset = 6) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_007(int value, int offset = 7) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_008(int value, int offset = 8) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_009(int value, int offset = 0) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_010(int value, int offset = 1) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_011(int value, int offset = 2) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_012(int value, int offset = 3) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_013(int value, int offset = 4) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_014(int value, int offset = 5) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_015(int value, int offset = 6) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_016(int value, int offset = 7) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_017(int value, int offset = 8) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_018(int value, int offset = 0) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_019(int value, int offset = 1) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_020(int value, int offset = 2) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_021(int value, int offset = 3) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_022(int value, int offset = 4) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_023(int value, int offset = 5) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_024(int value, int offset = 6) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_025(int value, int offset = 7) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_026(int value, int offset = 8) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_027(int value, int offset = 0) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_028(int value, int offset = 1) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_029(int value, int offset = 2) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_030(int value, int offset = 3) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_031(int value, int offset = 4) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_032(int value, int offset = 5) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_033(int value, int offset = 6) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_034(int value, int offset = 7) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_035(int value, int offset = 8) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_036(int value, int offset = 0) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_037(int value, int offset = 1) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_038(int value, int offset = 2) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_039(int value, int offset = 3) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_040(int value, int offset = 4) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_041(int value, int offset = 5) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_042(int value, int offset = 6) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_043(int value, int offset = 7) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_044(int value, int offset = 8) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_045(int value, int offset = 0) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_046(int value, int offset = 1) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_047(int value, int offset = 2) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_048(int value, int offset = 3) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_049(int value, int offset = 4) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_050(int value, int offset = 5) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_051(int value, int offset = 6) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_052(int value, int offset = 7) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_053(int value, int offset = 8) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_054(int value, int offset = 0) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_055(int value, int offset = 1) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_056(int value, int offset = 2) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_057(int value, int offset = 3) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_058(int value, int offset = 4) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_059(int value, int offset = 5) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_060(int value, int offset = 6) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_061(int value, int offset = 7) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_062(int value, int offset = 8) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_063(int value, int offset = 0) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_064(int value, int offset = 1) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_065(int value, int offset = 2) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_066(int value, int offset = 3) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_067(int value, int offset = 4) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_068(int value, int offset = 5) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_069(int value, int offset = 6) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_070(int value, int offset = 7) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_071(int value, int offset = 8) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_072(int value, int offset = 0) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_073(int value, int offset = 1) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_074(int value, int offset = 2) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_075(int value, int offset = 3) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_076(int value, int offset = 4) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_077(int value, int offset = 5) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_078(int value, int offset = 6) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_079(int value, int offset = 7) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_080(int value, int offset = 8) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_081(int value, int offset = 0) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_082(int value, int offset = 1) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_083(int value, int offset = 2) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_084(int value, int offset = 3) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_085(int value, int offset = 4) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_086(int value, int offset = 5) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_087(int value, int offset = 6) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_088(int value, int offset = 7) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_089(int value, int offset = 8) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_090(int value, int offset = 0) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_091(int value, int offset = 1) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_092(int value, int offset = 2) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_093(int value, int offset = 3) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_094(int value, int offset = 4) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_095(int value, int offset = 5) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_096(int value, int offset = 6) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_097(int value, int offset = 7) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_098(int value, int offset = 8) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_099(int value, int offset = 0) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_100(int value, int offset = 1) {
    int result = value + offset + 0;
    return result;
}

int basics_utility_101(int value, int offset = 2) {
    int result = value + offset + 1;
    return result;
}

int basics_utility_102(int value, int offset = 3) {
    int result = value + offset + 2;
    return result;
}

int basics_utility_103(int value, int offset = 4) {
    int result = value + offset + 3;
    return result;
}

int basics_utility_104(int value, int offset = 5) {
    int result = value + offset + 4;
    return result;
}

int basics_utility_105(int value, int offset = 6) {
    int result = value + offset + 0;
    return result;
}

// ---- Deliberate defects below ----

int main() {
    int base = add_numbers(10, 20);
    int extra = basics_utility_001(5, 6);
    int total = base + extra
    cout << "Total is: " << totl << endl;
    return 0;
}
