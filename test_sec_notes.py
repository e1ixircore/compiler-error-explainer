# test_security_notes.py - SECURITY NOTES + ERRORS: nothing here is dangerous enough to block, so the code is
# still analysed. The security notes appear in red above the corrections.
import tempfile
import socket                        # MEDIUM: network access

password = 'hunter2'                 # LOW: hardcoded secret

def main():
    path = tempfile.mktemp()         # MEDIUM: insecure temporary file name
    with open('notes.txt', 'w') as f:    # MEDIUM: writes a file
        f.write('hi')
    print(pasword)                   # ERROR: NameError (typo of 'password')
    print(5 / 0)                     # ERROR: ZeroDivisionError

if __name__ == '__main__':
    main()