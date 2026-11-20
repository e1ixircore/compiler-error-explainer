# test5.py - Beginner Identifier & Literal Mistakes (3 Fixable Errors)
def main():
    message = "Hello, world!"
    # ERROR 1 (NameError - fixable): typo 'mesage' -> 'message'
    print(mesage)
    # ERROR 2 (NameError - fixable): lowercase 'true' instead of Python's 'True'
    is_complete = true
    # ERROR 3 (TypeError - fixable): joining string and number without str()
    status_line = "Completion code: " + 1
    print(is_complete, status_line)

if __name__ == "__main__":
    main()
