# test5.py - Target: typo in a variable name (NameError + "did you mean")
def calculate_total(price, quantity):
    total_price = price * quantity
    return totl_price  # ERROR: typo, should be total_price

print(calculate_total(10, 3))