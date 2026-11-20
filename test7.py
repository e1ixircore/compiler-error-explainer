# test7.py - Control Flow, Types & Runtime Division by Zero (5 Fixable Errors)
def classify_temperature(temp):
    if temp > 100:
        return "boiling"
    # ERROR 1 (SyntaxError - fixable): 'else if' instead of Python's 'elif'
    else if temp > 50:
        return "warm"
    return "cool"

def build_age_message():
    # ERROR 2 (TypeError - fixable): concatenating str and int
    msg = "Age: " + 25
    return msg

def compute_moving_average():
    readings = [10, 20, 30]
    # ERROR 3 (IndexError - fixable): index 6 is out of bounds for 3-element list
    peak = readings[6]
    # ERROR 4 (NameError - fixable): typo 'readngs' -> 'readings'
    return peak + len(readngs)

def runtime_rate_calculation():
    deltas = [5, -5]
    # ERROR 5 (ZeroDivisionError - runtime fixable): divisor evaluates to 0 at runtime
    divisor = sum(deltas)
    return 200 / divisor

def main():
    print(classify_temperature(60))
    print(build_age_message())
    print(compute_moving_average())
    print(runtime_rate_calculation())

if __name__ == "__main__":
    main()
