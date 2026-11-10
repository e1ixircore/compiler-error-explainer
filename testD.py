# testD.py - TWO ERRORS ON ONE LINE: the code panel shows a "2" badge on the print(scorse, totl) line.
def report():
    scores = [90, 80, 70]
    total = sum(scores)
    average = total / len(scores)
    print(scorse, totl)              # ERRORS: two typos on the same line (NameError x2)
    print('Average: ' + 5)           # ERROR: TypeError (text + number)
    print(10 // 0)                   # ERROR: ZeroDivisionError

report()