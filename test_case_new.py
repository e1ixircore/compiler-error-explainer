import os
import sys
import json
import math
import random
import pandas as pd
import numpy as np

# -------------------------------
# GLOBAL VARIABLES
# -------------------------------
students_db = {}
courses_db = []
LOG_FILE = "log.txt"

# -------------------------------
# UTILITY FUNCTIONS
# -------------------------------

def log_message(msg):
    with open(LOG_FILE, "a") as file:
        file.write(msg + "\n")


def generate_id():
    return random.randint(1000, 9999)


def validate_email(email):
    if "@" not in email:
        return False
    if "." not in email:
        return False
    return True


# -------------------------------
# STUDENT CLASS
# -------------------------------

class Student:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email
        self.id = generate_id()

    def display(self):
        print("Name:", self.name)
        print("Age:", self.age)
        print("Email:", self.email)
        print("ID:", self.id)

    def is_adult(self):
        if self.age > 18:
            return True
        else:
            return False

    def update_email(self, new_email):
        if validate_email(new_email):
            self.email = new_email
        else:
            print("Invalid email")

# -------------------------------
# COURSE CLASS
# -------------------------------

class Course:
    def __init__(self, name, credits):
        self.name = name
        self.credits = credits

    def display(self):
        print("Course:", self.name)
        print("Credits:", self.credits)

# -------------------------------
# DATABASE FUNCTIONS
# -------------------------------

def add_student(student):
    students_db[student.id] = student
    log_message("Student added: " + student.name)


def remove_student(student_id):
    if student_id in students_db:
        del students_db[student_id]
    else:
        print("Student not found")


def get_student(student_id):
    return students_db.get(student_id)


def list_students():
    for s in students_db.values():
        s.display()


# -------------------------------
# FILE HANDLING
# -------------------------------

def save_to_file(filename):
    data = []
    for s in students_db.values():
        data.append({
            "name": s.name,
            "age": s.age,
            "email": s.email
        })

    with open(filename, "w") as f:
        json.dump(data, f)


def load_from_file(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return

    with open(filename, "r") as f:
        data = json.load(f)

    for item in data:
        s = Student(item.get("name", "Unknown"), item.get("age", 0), item.get("email", "unknown@mail.com"))
        add_student(s)


# -------------------------------
# MATH MODULE
# -------------------------------

def calculate_average(marks):
    if not marks:
        return 0
    total = 0
    for m in marks:
        total += m
    return total / len(marks)


def calculate_std(marks):
    if not marks:
        return 0
    mean = calculate_average(marks)
    variance = sum((x - mean)**2 for x in marks) / len(marks)
    return math.sqrt(variance)


# -------------------------------
# MACHINE LEARNING MOCK
# -------------------------------

class SimpleModel:
    def __init__(self):
        self.weights = None

    def train(self, X, y):
        self.weights = np.dot(np.linalg.inv(np.dot(X.T, X)), np.dot(X.T, y))

    def predict(self, X):
        return np.dot(X, self.weights)

    def evaluate(self, X, y):
        preds = self.predict(X)
        error = np.mean((preds - y)**2)
        return error


def load_dataset():
    if not os.path.exists("data.csv"):
        print("Error: data.csv not found.")
        return None, None
    df = pd.read_csv("data.csv")
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    return X, y


# -------------------------------
# API SIMULATION
# -------------------------------

def fetch_data_from_api(url):
    import requests
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"API request failed: {e}")
        return []


def process_api_data(data):
    for item in data:
        print(item.get("name", "Unknown Name"))


# -------------------------------
# STRING PROCESSING
# -------------------------------

def clean_text(text):
    text = text.lower()
    text = text.replace(",", "")
    text = text.replace(".", "")
    return text


def word_count(text):
    words = text.split(" ")
    return len(words)


def most_common_word(text):
    words = text.split()
    if not words:
        return None
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return max(freq, key=freq.get)


# -------------------------------
# SORTING
# -------------------------------

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                temp = arr[j]
                arr[j] = arr[j+1]
                arr[j+1] = temp
    return arr


# -------------------------------
# SEARCH
# -------------------------------

def linear_search(arr, key):
    for i in range(len(arr)):
        if arr[i] == key:
            return i
    return -1


def binary_search(arr, key):
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == key:
            return mid
        elif arr[mid] < key:
            left = mid + 1
        else:
            right = mid - 1
    return -1


# -------------------------------
# MULTITHREADING
# -------------------------------

import threading

def worker():
    print("Thread running")

def run_threads():
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker)
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()


# -------------------------------
# ERROR HANDLING
# -------------------------------

def risky_division(a, b):
    try:
        return a / b
    except ZeroDivisionError as e:
        print(f"ZeroDivisionError: Division by zero is not allowed.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# -------------------------------
# MAIN PROGRAM
# -------------------------------

def main():
    s1 = Student("Alice", 20, "alice@mail.com")
    s2 = Student("Bob", 17, "bobmail.com")  # invalid email

    add_student(s1)
    add_student(s2)

    list_students()

    save_to_file("students.json")

    load_from_file("students.json")

    marks = [10, 20, 30]
    print(calculate_average(marks))
    print(calculate_std(marks))

    X, y = load_dataset()
    if X is not None and y is not None:
        model = SimpleModel()
        model.train(X, y)
        preds = model.predict(X)
        print(preds)

    print(most_common_word("hello hello world"))

    arr = [5, 2, 9, 1]
    print(bubble_sort(arr))

    print(binary_search(sorted(arr), 2))

    run_threads()

    risky_division(10, 0)


if __name__ == "__main__":
    main()
