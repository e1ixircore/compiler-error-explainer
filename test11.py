# test11.py - STRESS TEST: 12 independent errors (3 NameError typos, 3 TypeError, 2 ZeroDivision,
# 2 IndexError, 2 KeyError). Static errors are fixed first; the runtime ones need execution each.
def main():
    scores = [90, 80, 70]
    prices = {'apple': 3, 'pear': 2}
    total = sum(scores)
    print(scorse)           # NameError (typo)
    print(totl)             # NameError (typo)
    print(pricse)           # NameError (typo)
    print('a' + 1)          # TypeError
    print('b' + 2)          # TypeError
    print('c' + 3)          # TypeError
    print(10 / 0)           # ZeroDivisionError
    print(5 // 0)           # ZeroDivisionError
    print(scores[10])       # IndexError (runtime)
    print(scores[20])       # IndexError (runtime)
    print(prices['kiwi'])   # KeyError (runtime)
    print(prices['plum'])   # KeyError (runtime)

if __name__ == '__main__':
    main()