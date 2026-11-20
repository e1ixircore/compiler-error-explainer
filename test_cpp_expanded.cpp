// test_cpp_expanded.cpp - Comprehensive C++ Diagnostic & Auto-Fix Showcase
// Covers structs, pointers, const-correctness, templates, STL headers, and function calls.
#include <iostream>
#include <vector>
#include <string>

struct SensorReading {
    int id;
    double value;
}  // Missing semicolon after struct definition

int compute_bonus(int base, int multiplier) {
    return base * multiplier;
}

void log_status(int code) {
    if (code = 200) {  // Assignment in condition
        std::cout << "OK" << std::endl;
    }
    return code;  // Returning a value from a void function
}

int inspect_sensor(SensorReading* ptr, SensorReading obj) {
    int a = ptr.id;          // Pointer accessed with '.' instead of '->'
    double b = obj->value;   // Value object accessed with '->' instead of '.'
    return a + static_cast<int>(b);
}

void demo_containers_and_types() {
    vector<int> scores = {30, 10, 20};   // Missing std:: prefix
    scores.push_bak(40);                 // Misspelled member name
    std::sort(scores.begin(), scores.end());  // Missing <algorithm> include
    string label = "Final";              // Missing std:: prefix
    std::cout << label << ": " << scores.size() << std::endl;

    std::vector raw_list;                // Missing template type argument <int>
    (void)raw_list;
}

void demo_const_and_operators() {
    const int max_retries = 5;
    max_retries = 10;        // Modifying a const variable

    int plain_num = 42;
    int deref = *plain_num;  // Dereferencing a non-pointer
    int indexed = plain_num[0];  // Subscripting a non-array
    int called = plain_num();    // Calling a non-function variable
    int wrong_args = compute_bonus(10);  // Too few arguments
    std::cout << deref << indexed << called << wrong_args << std::endl;
}

int main() {
    SensorReading r{1, 98.5};
    inspect_sensor(&r, r);
    demo_containers_and_types();
    demo_const_and_operators();
    log_status(200);
    return 0;
}
