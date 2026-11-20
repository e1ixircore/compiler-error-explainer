# test4.py - Bounds, Conversions & Assertion Logic Errors (4 Fixable Errors)
import math

def read_sensor_window():
    my_list = [12, 24, 36]
    # ERROR 1 (IndexError - fixable): index 10 is out of range for a 3-item list
    x = my_list[10]
    return x

def count_identifier_digits():
    serial_number = 54321
    # ERROR 2 (TypeError - fixable): len() cannot be called directly on an integer
    return len(serial_number)

def parse_step_count():
    # ERROR 3 (ValueError - fixable): '3.5' is a decimal string and cannot be passed directly to int()
    steps = int("3.5")
    return steps

def validate_positive_batch(batch_size):
    # ERROR 4 (LogicalError - fixable): assert(cond, msg) tests a 2-tuple which is always True!
    assert (batch_size > 0, "batch_size must be positive")
    return batch_size

def main():
    print("Sensor:", read_sensor_window())
    print("Digits:", count_identifier_digits())
    print("Steps:", parse_step_count())
    print("Validated:", validate_positive_batch(5))

if __name__ == "__main__":
    main()
