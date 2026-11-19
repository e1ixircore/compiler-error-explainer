// test_cpp_security.cpp - 550+ lines with a critical security finding (must be BLOCKED)
#include <cstdlib>
#include <iostream>

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

int sec_utility_001(int value, int offset = 1) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_002(int value, int offset = 2) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_003(int value, int offset = 3) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_004(int value, int offset = 4) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_005(int value, int offset = 5) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_006(int value, int offset = 6) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_007(int value, int offset = 7) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_008(int value, int offset = 8) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_009(int value, int offset = 0) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_010(int value, int offset = 1) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_011(int value, int offset = 2) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_012(int value, int offset = 3) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_013(int value, int offset = 4) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_014(int value, int offset = 5) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_015(int value, int offset = 6) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_016(int value, int offset = 7) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_017(int value, int offset = 8) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_018(int value, int offset = 0) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_019(int value, int offset = 1) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_020(int value, int offset = 2) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_021(int value, int offset = 3) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_022(int value, int offset = 4) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_023(int value, int offset = 5) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_024(int value, int offset = 6) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_025(int value, int offset = 7) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_026(int value, int offset = 8) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_027(int value, int offset = 0) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_028(int value, int offset = 1) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_029(int value, int offset = 2) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_030(int value, int offset = 3) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_031(int value, int offset = 4) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_032(int value, int offset = 5) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_033(int value, int offset = 6) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_034(int value, int offset = 7) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_035(int value, int offset = 8) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_036(int value, int offset = 0) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_037(int value, int offset = 1) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_038(int value, int offset = 2) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_039(int value, int offset = 3) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_040(int value, int offset = 4) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_041(int value, int offset = 5) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_042(int value, int offset = 6) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_043(int value, int offset = 7) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_044(int value, int offset = 8) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_045(int value, int offset = 0) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_046(int value, int offset = 1) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_047(int value, int offset = 2) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_048(int value, int offset = 3) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_049(int value, int offset = 4) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_050(int value, int offset = 5) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_051(int value, int offset = 6) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_052(int value, int offset = 7) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_053(int value, int offset = 8) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_054(int value, int offset = 0) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_055(int value, int offset = 1) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_056(int value, int offset = 2) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_057(int value, int offset = 3) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_058(int value, int offset = 4) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_059(int value, int offset = 5) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_060(int value, int offset = 6) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_061(int value, int offset = 7) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_062(int value, int offset = 8) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_063(int value, int offset = 0) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_064(int value, int offset = 1) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_065(int value, int offset = 2) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_066(int value, int offset = 3) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_067(int value, int offset = 4) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_068(int value, int offset = 5) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_069(int value, int offset = 6) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_070(int value, int offset = 7) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_071(int value, int offset = 8) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_072(int value, int offset = 0) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_073(int value, int offset = 1) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_074(int value, int offset = 2) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_075(int value, int offset = 3) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_076(int value, int offset = 4) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_077(int value, int offset = 5) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_078(int value, int offset = 6) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_079(int value, int offset = 7) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_080(int value, int offset = 8) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_081(int value, int offset = 0) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_082(int value, int offset = 1) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_083(int value, int offset = 2) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_084(int value, int offset = 3) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_085(int value, int offset = 4) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_086(int value, int offset = 5) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_087(int value, int offset = 6) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_088(int value, int offset = 7) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_089(int value, int offset = 8) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_090(int value, int offset = 0) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_091(int value, int offset = 1) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_092(int value, int offset = 2) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_093(int value, int offset = 3) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_094(int value, int offset = 4) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_095(int value, int offset = 5) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_096(int value, int offset = 6) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_097(int value, int offset = 7) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_098(int value, int offset = 8) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_099(int value, int offset = 0) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_100(int value, int offset = 1) {
    int result = value + offset + 0;
    return result;
}

int sec_utility_101(int value, int offset = 2) {
    int result = value + offset + 1;
    return result;
}

int sec_utility_102(int value, int offset = 3) {
    int result = value + offset + 2;
    return result;
}

int sec_utility_103(int value, int offset = 4) {
    int result = value + offset + 3;
    return result;
}

int sec_utility_104(int value, int offset = 5) {
    int result = value + offset + 4;
    return result;
}

int sec_utility_105(int value, int offset = 6) {
    int result = value + offset + 0;
    return result;
}

int run_diagnostics() {
    int val = sec_utility_050(10, 2);
    std::system("echo should_be_blocked");  // CRITICAL: command injection
    return val;
}

int main() {
    std::cout << run_diagnostics() << std::endl;
    return 0;
}
