# test1.py - Beginner Arithmetic, String & Condition Errors (4 Fixable Errors)
import sys
import math

def helper_func_0(val):
    res = val * 2
    for i in range(3):
        res += i
    return res

def process_data_0(data):
    temp = []
    for item in data:
        temp.append(helper_func_0(item))
    return temp

def check_pipeline_mode(mode_name):
    # ERROR 1 (LogicalError - fixable): using 'is' instead of '==' to compare with a string literal
    if mode_name is "active":
        return True
    return False

def format_summary_label(count):
    # ERROR 2 (TypeError - fixable): concatenating string and integer with '+'
    banner = "Processed items: " + 25
    return banner

def compute_discount_rate():
    # ERROR 3 (NameError - fixable): typo in variable name 'base_rate' -> 'base_rtae'
    base_rate = 15
    return base_rtae * 2

def main():
    print("Running test1 pipeline...")
    check_pipeline_mode("active")
    print(format_summary_label(25))
    print(compute_discount_rate())
    # ERROR 4 (ZeroDivisionError - fixable): dividing by literal zero
    x = 100 / 0
    print("Ratio:", x)

if __name__ == "__main__":
    main()
