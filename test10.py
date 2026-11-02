# test10.py - MULTI-ERROR demo: three independent errors, so the repair loop needs several passes.
# Pass 1 fixes the TypeError, pass 2 the NameError typo, pass 3 the runtime KeyError.
def main():
    prices = {'apple': 3}
    print('Total: ' + 5)        # ERROR 1: TypeError (found statically)
    print(prces)                # ERROR 2: NameError, typo of 'prices' (found statically)
    print(prices['pear'])       # ERROR 3: KeyError (only found by running the code)

if __name__ == '__main__':
    main()