# test6.py - Dictionary Lookups & Logical Comparison Bugs (4 Fixable, 1 Ambiguous)
def lookup_user_role():
    my_dict = {"a": 1, "b": 2}
    # ERROR 1 (KeyError - fixable): key 'c' is not present in my_dict
    val = my_dict["c"]
    # ERROR 2 (NameError - fixable): typo 'my_dcit' -> 'my_dict'
    return val, len(my_dcit)

def format_level_badge():
    # ERROR 3 (TypeError - fixable): string + int concatenation
    return "Security Level " + 4

def check_run_mode(label):
    # ERROR 4 (LogicalError - fixable): identity operator 'is' used with string literal
    if label is "production":
        return 1
    return 0

def verify_safety_limit(current_temp, max_temp):
    # ERROR 5 (Ambiguous LogicalError - manual fix needed): comparing 'current_temp' to itself
    # always evaluates to True! Edit the line below to compare current_temp against max_temp.
    if current_temp == current_temp:
        return "Within limit"
    return "Overheated"

def main():
    print(lookup_user_role())
    print(format_level_badge())
    print(check_run_mode("production"))
    print(verify_safety_limit(85, 70))

if __name__ == "__main__":
    main()
