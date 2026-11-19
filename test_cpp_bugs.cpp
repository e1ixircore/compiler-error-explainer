// test_cpp_bugs.cpp - 580+ lines with 10 deliberate C++ defect sites
// Defects:
//   1. Header typo (#include <iostrem>)
//   2. Return type mismatch (int returning const char*)
//   3. Missing return in non-void function
//   4. Division by zero (-Wdivision-by-zero)
//   5. Array out-of-bounds (-Warray-bounds)
//   6. Variable type mismatch (int = const char*)
//   7. Assignment in condition (if (x = 5))
//   8. Undeclared variable
//   9. Invalid main signature (void main())
//  10. Reversed stream operator (std::cout >> ...)

#include <iostrem>  // DEFECT 1: misspelled header name

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

int bugs_utility_001(int value, int offset = 1) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_002(int value, int offset = 2) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_003(int value, int offset = 3) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_004(int value, int offset = 4) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_005(int value, int offset = 5) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_006(int value, int offset = 6) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_007(int value, int offset = 7) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_008(int value, int offset = 8) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_009(int value, int offset = 0) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_010(int value, int offset = 1) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_011(int value, int offset = 2) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_012(int value, int offset = 3) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_013(int value, int offset = 4) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_014(int value, int offset = 5) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_015(int value, int offset = 6) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_016(int value, int offset = 7) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_017(int value, int offset = 8) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_018(int value, int offset = 0) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_019(int value, int offset = 1) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_020(int value, int offset = 2) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_021(int value, int offset = 3) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_022(int value, int offset = 4) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_023(int value, int offset = 5) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_024(int value, int offset = 6) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_025(int value, int offset = 7) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_026(int value, int offset = 8) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_027(int value, int offset = 0) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_028(int value, int offset = 1) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_029(int value, int offset = 2) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_030(int value, int offset = 3) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_031(int value, int offset = 4) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_032(int value, int offset = 5) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_033(int value, int offset = 6) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_034(int value, int offset = 7) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_035(int value, int offset = 8) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_036(int value, int offset = 0) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_037(int value, int offset = 1) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_038(int value, int offset = 2) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_039(int value, int offset = 3) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_040(int value, int offset = 4) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_041(int value, int offset = 5) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_042(int value, int offset = 6) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_043(int value, int offset = 7) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_044(int value, int offset = 8) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_045(int value, int offset = 0) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_046(int value, int offset = 1) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_047(int value, int offset = 2) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_048(int value, int offset = 3) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_049(int value, int offset = 4) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_050(int value, int offset = 5) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_051(int value, int offset = 6) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_052(int value, int offset = 7) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_053(int value, int offset = 8) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_054(int value, int offset = 0) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_055(int value, int offset = 1) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_056(int value, int offset = 2) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_057(int value, int offset = 3) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_058(int value, int offset = 4) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_059(int value, int offset = 5) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_060(int value, int offset = 6) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_061(int value, int offset = 7) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_062(int value, int offset = 8) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_063(int value, int offset = 0) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_064(int value, int offset = 1) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_065(int value, int offset = 2) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_066(int value, int offset = 3) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_067(int value, int offset = 4) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_068(int value, int offset = 5) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_069(int value, int offset = 6) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_070(int value, int offset = 7) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_071(int value, int offset = 8) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_072(int value, int offset = 0) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_073(int value, int offset = 1) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_074(int value, int offset = 2) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_075(int value, int offset = 3) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_076(int value, int offset = 4) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_077(int value, int offset = 5) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_078(int value, int offset = 6) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_079(int value, int offset = 7) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_080(int value, int offset = 8) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_081(int value, int offset = 0) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_082(int value, int offset = 1) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_083(int value, int offset = 2) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_084(int value, int offset = 3) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_085(int value, int offset = 4) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_086(int value, int offset = 5) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_087(int value, int offset = 6) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_088(int value, int offset = 7) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_089(int value, int offset = 8) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_090(int value, int offset = 0) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_091(int value, int offset = 1) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_092(int value, int offset = 2) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_093(int value, int offset = 3) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_094(int value, int offset = 4) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_095(int value, int offset = 5) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_096(int value, int offset = 6) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_097(int value, int offset = 7) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_098(int value, int offset = 8) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_099(int value, int offset = 0) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_100(int value, int offset = 1) {
    int result = value + offset + 0;
    return result;
}

int bugs_utility_101(int value, int offset = 2) {
    int result = value + offset + 1;
    return result;
}

int bugs_utility_102(int value, int offset = 3) {
    int result = value + offset + 2;
    return result;
}

int bugs_utility_103(int value, int offset = 4) {
    int result = value + offset + 3;
    return result;
}

int bugs_utility_104(int value, int offset = 5) {
    int result = value + offset + 4;
    return result;
}

int bugs_utility_105(int value, int offset = 6) {
    int result = value + offset + 0;
    return result;
}

// ---- Deliberate defects: 10 total in this file ----

int defect_02_bad_return() {
    return "wrong";  // DEFECT 2: return type mismatch
}

int defect_03_missing_return(int x) {
    int y = x + 1;
    (void)y;
}  // DEFECT 3: non-void function missing return

int defect_04_div_zero() {
    return 10 / 0;  // DEFECT 4: division by zero
}

int defect_05_array_oob() {
    int arr[3] = {10, 20, 30};
    return arr[10];  // DEFECT 5: array index out of bounds
}

int defect_06_type_assign() {
    int count = "many";  // DEFECT 6: incompatible initializer type
    return count;
}

int defect_07_assign_in_cond(int x) {
    if (x = 5) {  // DEFECT 7: assignment used as condition
        return x;
    }
    return 0;
}

int defect_08_undeclared() {
    return missing_cpp_var;  // DEFECT 8: undeclared identifier
}

void main() {  // DEFECT 9: main must return int
    int sum = add_numbers(2, 3) + bugs_utility_001(4, 1);
    std::cout >> sum << " "  // DEFECT 10: reversed stream operator
              << defect_02_bad_return() << " "
              << defect_03_missing_return(1) << " "
              << defect_04_div_zero() << " "
              << defect_05_array_oob() << " "
              << defect_06_type_assign() << " "
              << defect_07_assign_in_cond(5) << " "
              << defect_08_undeclared() << std::endl;
}
