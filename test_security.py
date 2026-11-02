import os
import tempfile

# -----------------------------------------------
# SECURITY VULNERABILITY DEMONSTRATION FILE
# This file intentionally contains security issues
# to demonstrate the pre-execution scanner.
# -----------------------------------------------

# VULNERABILITY 1 [CRITICAL]: Command Injection
# os.system passes strings directly to the shell
def delete_files():
    os.system("rm -rf /tmp/test")  # Dangerous shell command

# VULNERABILITY 2 [HIGH]: Arbitrary Code Execution
# eval() can run any string as Python code
def run_user_input(user_data):
    result = eval(user_data)  # Attacker controls execution
    return result

# VULNERABILITY 3 [MEDIUM]: Insecure Temporary File
# mktemp() is vulnerable to race-condition hijacking
def create_temp():
    tmp = tempfile.mktemp()  # Insecure - use mkstemp() instead
    return tmp

# VULNERABILITY 4 [LOW]: Hardcoded Secret / API Key
password = "admin123"       # Plaintext password in source code
api_key = "sk-abc123xyz"    # Hardcoded API key exposed

# MAIN
def main():
    print("Running vulnerable code demo...")
    create_temp()
    run_user_input("2 + 2")
    delete_files()

if __name__ == "__main__":
    main()
