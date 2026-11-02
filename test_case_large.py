import json
import random
import math
import datetime
import threading

# ----------------------------------
# GLOBAL DATA
# ----------------------------------
data_store = []
results = []

# ----------------------------------
# DATA CLASS
# ----------------------------------
class DataPoint:
    def __init__(self, value):
        self.value = value
        self.timestamp = datetime.datetime.now()

    def display(self):
        print("Value:", self.value, "| Time:", self.timestamp)


# ----------------------------------
# DATA GENERATION
# ----------------------------------
def generate_data(n):
    for i in range(n):
        val = random.randint(1, 100)
        dp = DataPoint(val)
        data_store.append(dp)


# ----------------------------------
# DATA PROCESSING
# ----------------------------------
def get_values():
    return [d.value for d in data_store]


def compute_sum(values):
    total = 0
    for v in values:
        total += v
    return total


def compute_mean(values):
    if len(values) == 0:
        return 0
    return compute_sum(values) / len(values)


def compute_variance(values):
    mean = compute_mean(values)
    total = 0
    for v in values:
        total += (v - mean) ** 2
    return total / len(values)


def compute_std(values):
    return math.sqrt(compute_variance(values))


# ----------------------------------
# FILTERING
# ----------------------------------
def filter_even(values):
    return [v for v in values if v % 2 == 0]


def filter_odd(values):
    return [v for v in values if v % 2 != 0]


# ----------------------------------
# SORTING
# ----------------------------------
def bubble_sort(arr):
    arr = arr[:]
    for i in range(len(arr)):
        for j in range(len(arr) - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


# ----------------------------------
# SEARCH
# ----------------------------------
def linear_search(arr, key):
    for i in range(len(arr)):
        if arr[i] == key:
            return i
    return -1


# ----------------------------------
# TRANSFORMATIONS
# ----------------------------------
def square_values(values):
    return [v * v for v in values]


def cube_values(values):
    return [v ** 3 for v in values]


# ----------------------------------
# FILE OPERATIONS
# ----------------------------------
def save_data(filename):
    out = [d.value for d in data_store]
    with open(filename, "w") as f:
        json.dump(out, f)


def load_data(filename):
    with open(filename, "r") as f:
        values = json.load(f)

    for v in values:
        data_store.append(DataPoint(v))


# ----------------------------------
# MULTITHREADING
# ----------------------------------
def worker(values):
    s = compute_sum(values)
    results.append(s)


def run_threads(values):
    threads = []
    chunk_size = max(1, len(values) // 3)

    for i in range(0, len(values), chunk_size):
        chunk = values[i:i + chunk_size]
        t = threading.Thread(target=worker, args=(chunk,))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()


# ----------------------------------
# REPORTING
# ----------------------------------
def print_report(values):
    print("Total:", compute_sum(values))
    print("Mean:", compute_mean(values))
    print("Std Dev:", compute_std(values))


def print_sorted(values):
    sorted_vals = bubble_sort(values)
    print("Sorted:", sorted_vals)


def print_search(values):
    key = values[0]
    idx = linear_search(values, key)
    print("Search for", key, "found at index", idx)


# ----------------------------------
# ADVANCED ANALYTICS
# ----------------------------------
def max_value(values):
    return max(values)


def min_value(values):
    return min(values)


def range_value(values):
    return max_value(values) - min_value(values)


# ----------------------------------
# PIPELINE
# ----------------------------------
def processing_pipeline():
    values = get_values()

    evens = filter_even(values)
    odds = filter_odd(values)

    squared = square_values(values)
    cubed = cube_values(values)

    print("Even count:", len(evens))
    print("Odd count:", len(odds))

    print("Max:", max_value(values))
    print("Min:", min_value(values))
    print("Range:", range_value(values))

    print_report(values)
    print_sorted(values)
    print_search(values)

    run_threads(values)

    print("Thread sums:", results)

    print("Squared sample:", squared[:5])
    print("Cubed sample:", cubed[:5])


# ----------------------------------
# MAIN
# ----------------------------------
def main():
    generate_data(20)

    for d in data_store[:5]:
        d.display()

    processing_pipeline()

    save_data("data.json")
    load_data("data.json")

    values = get_values()

    print("Final Mean:", compute_mean(values))

    # 🔴 ONLY ERROR BELOW (recoverable)
    print("Final Result:", final_output)


if __name__ == "__main__":
    main()