# test_security_first.py - ORDER OF CHECKS: this file also has an ordinary NameError, but the security scan
# runs FIRST. The code is blocked, so the NameError is never reported.
import os

def main():
    print(mesage)                    # ERROR: NameError (never reported: blocked before analysis)
    os.system('echo hello')          # CRITICAL: command execution

if __name__ == '__main__':
    main()