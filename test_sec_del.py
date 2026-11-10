# test_security_delete.py - SECURITY: code that deletes files. (Paths are harmless, and the code is blocked anyway.)
import os
import shutil

def cleanup():
    shutil.rmtree('/tmp/intellifix_demo_folder')   # HIGH: deletes a whole folder
    os.remove('no_such_file.txt')                  # HIGH: deletes a file

cleanup()