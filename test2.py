# test2.py - Syntax Rules & List Indexing Errors (4 Fixable Errors)
import math

def compute_step_bonus(score):
    # ERROR 1 (SyntaxError - fixable): assignment '=' used instead of '==' in if condition
    if score = 100:
        return 50
    return 10

def verify_threshold(val)
    # ERROR 2 (SyntaxError - fixable): missing colon ':' at end of function definition above
    return val * 2

def pick_middle_element():
    samples = [10, 20, 30, 40, 50]
    # ERROR 3 (TypeError - fixable): single-slash division '/' produces a float index (2.0)
    mid = samples[4 / 2]
    # ERROR 4 (IndexError - fixable): off-by-one index len(samples) is past the end of the list
    last = samples[len(samples)]
    return mid, last

def main():
    print("Bonus:", compute_step_bonus(100))
    print("Threshold:", verify_threshold(12))
    print("Elements:", pick_middle_element())

if __name__ == "__main__":
    main()
