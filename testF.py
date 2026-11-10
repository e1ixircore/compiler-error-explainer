# test15.py - RUNTIME-ONLY ERRORS: none of these can be seen by reading the code, only by running it.
def main():
    scores = [70, 85, 90]
    profile = {'name': 'Asha', 'age': 17}
    print(scores[5])                 # ERROR: IndexError (list has only 3 items)
    print(profile['grade'])          # ERROR: KeyError (no 'grade' key)
    import missing_helper            # ERROR: ModuleNotFoundError (library does not exist)

if __name__ == '__main__':
    main()