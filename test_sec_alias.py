# test_security_alias.py - SECURITY: dangerous calls hidden behind nicknames. The scanner still sees them.
import os as o
from subprocess import run as r

def main():
    o.system('echo hello')           # CRITICAL: os.system hidden behind the nickname "o"
    r(['echo', 'hi'])                # CRITICAL: subprocess.run hidden behind the nickname "r"
    eval('1 + 1')                    # HIGH: eval runs any text as code

if __name__ == '__main__':
    main()