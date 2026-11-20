# test3.py - Mixed Static, Runtime & Ambiguous Scope Errors (4 Fixable, 1 Ambiguous)
import math

def summarize_inventory():
    # ERROR 1 (NameError - fixable): typo in variable name 'total_items' -> 'totl_items'
    total_items = 48
    return totl_items

def read_server_port():
    # ERROR 2 (KeyError - fixable): key 'port' does not exist in dictionary
    config = {"host": "127.0.0.1", "protocol": "https"}
    return config["port"]

def record_unique_tag():
    # ERROR 3 (AttributeError - fixable): sets use .add(), not .append()
    active_tags = {"alpha", "beta"}
    active_tags.append("gamma")
    return len(active_tags)

def calculate_calibrated_reading():
    # ERROR 4 (ZeroDivisionError - fixable): division by zero
    reading = 80 / 0
    return reading

def apply_custom_formula():
    base_val = 10
    # ERROR 5 (Ambiguous NameError - manual fix needed): 'custom_user_offset' has never been
    # defined and has no close spelling match. Use the inline code box to set your intended value!
    return base_val + custom_user_offset

def main():
    print("Inventory:", summarize_inventory())
    print("Port:", read_server_port())
    print("Tags:", record_unique_tag())
    print("Reading:", calculate_calibrated_reading())

if __name__ == "__main__":
    main()
