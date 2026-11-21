"""
test_sandbox.py - Verification and Security Test Suite for TOACD Sandbox
========================================================================
Validates that the sandbox prevents host compromise across all attack vectors:
- Host filesystem tampering / writes
- Sensitive credential / config reading
- Network socket communication / data exfiltration
- Process execution / shell spawning
- Infinite execution loops / resource starvation
And confirms normal, safe user code executes cleanly.
"""

import os
import platform
import subprocess
import sys
import tempfile
import unittest

from sandbox import (
    AuditHookSandboxEngine,
    DockerSandboxEngine,
    SandboxManager,
    SeatbeltSandboxEngine,
    get_sandbox_status,
    run_sandboxed_command,
    run_sandboxed_python,
)


class TestSandboxSecurity(unittest.TestCase):
    """Verifies isolation barriers and attack vector containment."""

    def test_sandbox_status_structure(self):
        status = get_sandbox_status()
        self.assertIn("active_engine", status)
        self.assertIn("active_details", status)
        self.assertIn("engines_available", status)
        self.assertIn("platform", status)
        self.assertTrue(status["active_details"].get("network_blocked"))
        self.assertTrue(status["active_details"].get("filesystem_writes_restricted"))

    def test_benign_python_execution(self):
        code = """
import math, sys, json
data = {"squared": [x ** 2 for x in range(5)], "sqrt_16": math.sqrt(16)}
print("DATA:" + json.dumps(data))
"""
        res = run_sandboxed_python(code, timeout=5)
        self.assertIsNone(res["error_type"])
        self.assertIn("DATA:", res["stdout"])
        self.assertIn('"sqrt_16": 4.0', res["stdout"])

    def test_filesystem_write_blocked_outside_scratch(self):
        # Attempt to create an unauthorized file in /tmp or system directories
        target_path = "/tmp/evil_sandbox_test.txt"
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
            except OSError:
                pass
        code = f"""
try:
    with open("{target_path}", "w") as f:
        f.write("COMPROMISED")
    print("WRITE_STATUS:COMPROMISED")
except Exception as e:
    print("WRITE_STATUS:BLOCKED:" + type(e).__name__)
"""
        try:
            res = run_sandboxed_python(code, timeout=5)
            self.assertIn("WRITE_STATUS:BLOCKED:", res["stdout"])
            self.assertFalse(os.path.exists(target_path))
        finally:
            if os.path.exists(target_path):
                try:
                    os.remove(target_path)
                except OSError:
                    pass

    def test_network_connection_blocked(self):
        code = """
try:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    s.connect(("8.8.8.8", 53))
    print("NET_STATUS:COMPROMISED")
except Exception as e:
    print("NET_STATUS:BLOCKED:" + type(e).__name__)
"""
        res = run_sandboxed_python(code, timeout=5)
        self.assertIn("NET_STATUS:BLOCKED:", res["stdout"])
        self.assertNotIn("NET_STATUS:COMPROMISED", res["stdout"])

    def test_subprocess_and_shell_execution_blocked(self):
        code = """
try:
    import subprocess
    p = subprocess.Popen(["/bin/echo", "HACKED"], stdout=subprocess.PIPE)
    out, _ = p.communicate()
    print("SUBPROCESS_STATUS:COMPROMISED")
except Exception as e:
    print("SUBPROCESS_STATUS:BLOCKED:" + type(e).__name__)
"""
        res = run_sandboxed_python(code, timeout=5)
        self.assertIn("SUBPROCESS_STATUS:BLOCKED:", res["stdout"])
        self.assertNotIn("SUBPROCESS_STATUS:COMPROMISED", res["stdout"])

    def test_os_system_blocked(self):
        target_path = "/tmp/hacked_sys.txt"
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
            except OSError:
                pass
        code = f"""
try:
    import os
    os.system("echo HACKED > {target_path}")
    print("SYSTEM_STATUS:CALLED")
except Exception as e:
    print("SYSTEM_STATUS:BLOCKED:" + type(e).__name__)
"""
        try:
            res = run_sandboxed_python(code, timeout=5)
            self.assertFalse(os.path.exists(target_path))
            self.assertIn("SYSTEM_STATUS:BLOCKED:PermissionError", res["stdout"])
        finally:
            if os.path.exists(target_path):
                try:
                    os.remove(target_path)
                except OSError:
                    pass

    def test_sensitive_credential_reading_blocked(self):
        ssh_path = os.path.expanduser("~/.ssh")
        code = f"""
import os
try:
    os.listdir("{ssh_path}")
    print("READ_STATUS:COMPROMISED")
except Exception as e:
    print("READ_STATUS:BLOCKED:" + type(e).__name__)
"""
        res = run_sandboxed_python(code, timeout=5)
        self.assertIn("READ_STATUS:BLOCKED:", res["stdout"])
        self.assertNotIn("READ_STATUS:COMPROMISED", res["stdout"])

    def test_execution_timeout_enforced(self):
        infinite_loop = """
while True:
    pass
"""
        res = run_sandboxed_python(infinite_loop, timeout=2)
        self.assertEqual(res["error_type"], "TimeoutError")
        self.assertIn("time limit", res["error_message"].lower())

    def test_scratch_directory_isolation(self):
        scratch = tempfile.mkdtemp(prefix="test_scratch_")
        code = f"""
import os, sys
scratch = "{os.path.realpath(scratch)}"
inside = os.path.join(scratch, "scratch_file.txt")
try:
    with open(inside, "w") as f:
        f.write("ALLOWED")
    print("INSIDE:OK")
except Exception as e:
    print("INSIDE:FAILED:" + str(e))
"""
        try:
            res = run_sandboxed_python(code, timeout=5, scratch_dir=scratch)
            self.assertIn("INSIDE:OK", res["stdout"])
            self.assertTrue(os.path.exists(os.path.join(scratch, "scratch_file.txt")))
        finally:
            import shutil
            shutil.rmtree(scratch, ignore_errors=True)

    def test_audithook_engine_directly(self):
        engine = AuditHookSandboxEngine()
        self.assertTrue(engine.is_available())
        res = engine.run_python("print('AUDIT_HOOK_OK')", timeout=5)
        self.assertIsNone(res["error_type"])
        self.assertIn("AUDIT_HOOK_OK", res["stdout"])

    def test_seatbelt_engine_directly_if_on_darwin(self):
        if platform.system() == "Darwin":
            engine = SeatbeltSandboxEngine()
            # If available (host or unsandboxed environment)
            if engine.is_available():
                res = engine.run_python("print('SEATBELT_OK')", timeout=5)
                self.assertIsNone(res["error_type"])
                self.assertIn("SEATBELT_OK", res["stdout"])
                self.assertIn("Seatbelt", res["sandbox_engine"])

    def test_cpp_sandboxed_execution(self):
        try:
            from cpp_extractor import run_cpp_code, find_compiler
            if not find_compiler():
                self.skipTest("No C++ compiler available")
            code = """
#include <iostream>
int main() {
    std::cout << "CPP_SANDBOX_OK" << std::endl;
    return 0;
}
"""
            res = run_cpp_code(code, timeout=5)
            self.assertIsNone(res["error_type"])
            self.assertIn("CPP_SANDBOX_OK", res["stdout"])
        except (ImportError, RuntimeError) as e:
            self.skipTest(f"C++ sandbox test skipped: {e}")


if __name__ == "__main__":
    unittest.main()
