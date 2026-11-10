# testE.py - SYNTAX CHAIN: Python reports only ONE syntax error at a time, so the tool fixes them one by one,
# then carries on to the other kinds of error.
def greet(name)                      # ERROR 1: SyntaxError (missing colon)
    print('Hello ' + name)

def main():
    for i in range(3)                # ERROR 2: SyntaxError (missing colon)
        greet('Sam')
    print(count)                     # ERROR 3: NameError (never created)
    items = [1, 2, 3]
    print(items[7])                  # ERROR 4: IndexError (found by running)

if __name__ == '__main__':
    main()