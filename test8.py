# test8.py - Module Imports, Indexing & Dictionary Errors (4 Fixable, 1 Ambiguous)
# ERROR 1 (ModuleNotFoundError - fixable): typo of standard library 'math' ('maths')
import maths

# ERROR 2 (Ambiguous ModuleNotFoundError - manual fix needed): non-existent third-party module
import non_existent_custom_sdk

def compute_circle_metrics():
    radius_val = 7
    # ERROR 3 (NameError - fixable): typo 'raduis_val' -> 'radius_val'
    area = 3.14159 * (raduis_val ** 2)
    return area

def get_center_bucket():
    buckets = [5, 10, 15, 20]
    # ERROR 4 (TypeError - fixable): float division '/' used as list index
    return buckets[2 / 2]

def load_timeout_setting():
    cfg = {"host": "localhost"}
    # ERROR 5 (KeyError - fixable): missing key 'timeout'
    return cfg["timeout"]

def main():
    print("Area:", compute_circle_metrics())
    print("Bucket:", get_center_bucket())
    print("Timeout:", load_timeout_setting())

if __name__ == "__main__":
    main()
