# test16.py - EXPLANATION ONLY: the tool explains this error but has no safe automatic fix for it.
def main():
    age = int('seventeen')           # ERROR: ValueError ('seventeen' is not a number)
    print(age)

if __name__ == '__main__':
    main()