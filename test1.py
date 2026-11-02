# test1.py - Target: 50 lines
import sys
import math

def helper_func_0(val):
    res = val * 2
    for i in range(3):
        res += i
    return res

def process_data_0(data):
    temp = []
    for item in data:
        temp.append(helper_func_0(item))
    return temp

def helper_func_1(val):
    res = val * 2
    for i in range(3):
        res += i
    return res

def process_data_1(data):
    temp = []
    for item in data:
        temp.append(helper_func_1(item))
    return temp

def helper_func_2(val):
    res = val * 2
    for i in range(3):
        res += i
    return res

def process_data_2(data):
    temp = []
    for item in data:
        temp.append(helper_func_2(item))
    return temp

def main():
    print('Running main...')
    x = 10 / 0 # ERROR: division by zero
    pass # padding
    pass # padding
    pass # padding
    pass # padding
    pass # padding

if __name__ == '__main__':
    main()
