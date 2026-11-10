# test_security_escape.py - SECURITY: tricks that try to reach dangerous functions indirectly.
import os
import ctypes                        # HIGH: can bypass Python's safety checks

def main():
    run = getattr(os, 'system')      # HIGH: getattr used to fetch os.system by name
    run('echo hello')
    print(().__class__.__bases__[0].__subclasses__())   # HIGH: well-known sandbox-escape trick

if __name__ == '__main__':
    main()