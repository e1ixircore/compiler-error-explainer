"""
tests/test_security_metrics.py
==============================
Automated unit test suite validating all 52 security metrics (SEC_01 .. SEC_52)
in SecurityMetricsEngine individually, plus registry integrity, zero-regression
comparison, syntax-error lexical fallback, and taxonomy exports.
"""

import math
import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from security_metrics_engine import METRICS_REGISTRY, SecurityMetricsEngine


class TestSecurityMetricsRegistry(unittest.TestCase):
    """Validates structural invariants of the 52-metric registry and exporters."""

    def setUp(self) -> None:
        self.engine = SecurityMetricsEngine()

    def test_registry_has_exact_52_metrics(self) -> None:
        self.assertEqual(len(METRICS_REGISTRY), 52)
        expected_ids = [f"SEC_{i:02d}" for i in range(1, 53)]
        self.assertEqual(list(METRICS_REGISTRY.keys()), expected_ids)

    def test_registry_specs_valid(self) -> None:
        valid_severities = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
        valid_kinds = {"detector", "quantitative"}
        for mid, spec in METRICS_REGISTRY.items():
            self.assertEqual(spec.id, mid)
            self.assertIn(spec.severity, valid_severities)
            self.assertIn(spec.kind, valid_kinds)
            self.assertTrue(spec.name)
            self.assertTrue(spec.category)
            self.assertTrue(spec.description)
            if spec.kind == "detector":
                self.assertGreater(spec.weight, 0.0)
            else:
                self.assertEqual(spec.weight, 0.0)

    def test_export_taxonomy_markdown_and_csv(self) -> None:
        md = self.engine.export_taxonomy_markdown()
        csv_text = self.engine.export_taxonomy_csv()
        for i in range(1, 53):
            mid = f"SEC_{i:02d}"
            self.assertIn(f"`{mid}`", md)
            self.assertIn(mid, csv_text)


class TestAll52SecurityMetrics(unittest.TestCase):
    """Tests each of the 52 security metrics (SEC_01 through SEC_52) individually."""

    def setUp(self) -> None:
        self.engine = SecurityMetricsEngine()

    def _assert_triggers(self, metric_id: str, code: str, language: str = "python") -> dict:
        report = self.engine.analyze(code, language=language)
        self.assertGreaterEqual(
            report["metrics"][metric_id],
            1,
            f"Expected {metric_id} to trigger on code:\n{code}",
        )
        self.assertIn(metric_id, report["triggered_metrics"])
        matching = [f for f in report["findings"] if f["metric_id"] == metric_id]
        self.assertTrue(matching, f"Expected finding entry for {metric_id}")
        spec = METRICS_REGISTRY[metric_id]
        self.assertEqual(matching[0]["cwe"], spec.cwe)
        self.assertEqual(matching[0]["severity"], spec.severity)
        return report

    def _assert_clean(self, metric_id: str, code: str, language: str = "python") -> dict:
        report = self.engine.analyze(code, language=language)
        self.assertEqual(
            report["metrics"][metric_id],
            0,
            f"Expected {metric_id} NOT to trigger on clean code:\n{code}",
        )
        self.assertNotIn(metric_id, report["triggered_metrics"])
        return report

    # --- Category 1: Injection & Execution (SEC_01 - SEC_08) ---

    def test_sec_01_os_command_injection(self) -> None:
        self._assert_triggers("SEC_01", 'import os\nos.system("echo hi")\n')
        self._assert_clean("SEC_01", "x = 1 + 2\n")

    def test_sec_02_dynamic_code_evaluation(self) -> None:
        self._assert_triggers("SEC_02", 'res = eval("2 + 2")\n')
        self._assert_clean("SEC_02", 'import ast\nres = ast.literal_eval("2")\n')

    def test_sec_03_insecure_deserialization(self) -> None:
        self._assert_triggers("SEC_03", "import pickle\nobj = pickle.loads(raw)\n")
        self._assert_clean("SEC_03", "import yaml\nobj = yaml.load(raw, Loader=yaml.SafeLoader)\n")

    def test_sec_04_raw_sql_injection(self) -> None:
        self._assert_triggers("SEC_04", 'cursor.execute(f"SELECT * FROM users WHERE id = {uid}")\n')
        self._assert_clean("SEC_04", 'cursor.execute("SELECT * FROM users WHERE id = %s", (uid,))\n')

    def test_sec_05_xml_external_entity(self) -> None:
        self._assert_triggers("SEC_05", "import xml.etree.ElementTree as ET\n")
        self._assert_clean("SEC_05", "import json\n")

    def test_sec_06_server_side_template_injection(self) -> None:
        self._assert_triggers(
            "SEC_06",
            "from flask import render_template_string\nout = render_template_string(user_tpl)\n",
        )
        self._assert_clean("SEC_06", 'out = "hello world"\n')

    def test_sec_07_ldap_xpath_injection(self) -> None:
        self._assert_triggers("SEC_07", "conn.search_s(base_dn, scope, user_filter)\n")
        self._assert_clean("SEC_07", 'conn.search_s("dc=example,dc=com", 2, "(uid=alice)")\n')

    def test_sec_08_unsafe_dynamic_import(self) -> None:
        self._assert_triggers("SEC_08", 'mod = __import__("math")\n')
        self._assert_clean("SEC_08", "import math\n")

    # --- Category 2: Sandbox Escape & Reflection (SEC_09 - SEC_14) ---

    def test_sec_09_mro_class_traversal(self) -> None:
        self._assert_triggers("SEC_09", "subs = ().__class__.__bases__[0].__subclasses__()\n")
        self._assert_clean("SEC_09", "x = (1, 2, 3)\n")

    def test_sec_10_builtins_namespace_poisoning(self) -> None:
        self._assert_triggers("SEC_10", '__builtins__["open"] = None\n')
        self._assert_clean("SEC_10", 'cfg = {"open": False}\n')

    def test_sec_11_frame_inspection(self) -> None:
        self._assert_triggers("SEC_11", "import sys\nframe = sys._getframe(0)\n")
        self._assert_clean("SEC_11", "import sys\nv = sys.version\n")

    def test_sec_12_native_code_binding(self) -> None:
        self._assert_triggers("SEC_12", "import ctypes\n")
        self._assert_clean("SEC_12", "import math\n")

    def test_sec_13_global_symbol_table_tampering(self) -> None:
        self._assert_triggers("SEC_13", 'globals()["injected"] = 1\n')
        self._assert_clean("SEC_13", "injected = 1\n")

    def test_sec_14_reflection_obfuscation(self) -> None:
        self._assert_triggers("SEC_14", 'fn = getattr(obj, "system")\n')
        self._assert_clean("SEC_14", 'val = getattr(obj, "normal_field", None)\n')

    # --- Category 3: File System & Path Traversal (SEC_15 - SEC_20) ---

    def test_sec_15_directory_path_traversal(self) -> None:
        self._assert_triggers("SEC_15", 'p = "../../secret.txt"\n')
        self._assert_clean("SEC_15", 'p = "data/report.txt"\n')

    def test_sec_16_destructive_file_operations(self) -> None:
        self._assert_triggers("SEC_16", 'import os\nos.remove("important.db")\n')
        self._assert_clean("SEC_16", 'import os\nexists = os.path.exists("important.db")\n')

    def test_sec_17_insecure_temporary_file(self) -> None:
        self._assert_triggers("SEC_17", "import tempfile\npath = tempfile.mktemp()\n")
        self._assert_clean("SEC_17", "import tempfile\nfd, path = tempfile.mkstemp()\n")

    def test_sec_18_sensitive_system_path_access(self) -> None:
        self._assert_triggers("SEC_18", 'target = "/etc/passwd"\n')
        self._assert_clean("SEC_18", 'target = "config/settings.json"\n')

    def test_sec_19_overly_permissive_file_permissions(self) -> None:
        self._assert_triggers("SEC_19", 'import os\nos.chmod("script.sh", 0o777)\n')
        self._assert_clean("SEC_19", 'import os\nos.chmod("script.sh", 0o600)\n')

    def test_sec_20_symlink_or_arbitrary_file_write(self) -> None:
        self._assert_triggers("SEC_20", 'f = open("output.txt", "w")\n')
        self._assert_clean("SEC_20", 'f = open("output.txt", "r")\n')

    # --- Category 4: Cryptography & Secrets (SEC_21 - SEC_27) ---

    def test_sec_21_hardcoded_credentials(self) -> None:
        self._assert_triggers("SEC_21", 'api_key = "super_secret_prod_key_12345"\n')
        self._assert_clean("SEC_21", 'import os\napi_key = os.environ.get("API_KEY", "")\n')

    def test_sec_22_weak_prng(self) -> None:
        self._assert_triggers("SEC_22", "import random\ntok = random.randint(1000, 9999)\n")
        self._assert_clean("SEC_22", "import secrets\ntok = secrets.randbelow(1000)\n")

    def test_sec_23_deprecated_hash_algorithm(self) -> None:
        self._assert_triggers("SEC_23", 'import hashlib\ndigest = hashlib.md5(b"data").hexdigest()\n')
        self._assert_clean("SEC_23", 'import hashlib\ndigest = hashlib.sha256(b"data").hexdigest()\n')

    def test_sec_24_weak_symmetric_cipher_or_ecb(self) -> None:
        self._assert_triggers("SEC_24", "cipher = AES.new(key, AES.MODE_ECB)\n")
        self._assert_clean("SEC_24", "cipher = AES.new(key, AES.MODE_GCM)\n")

    def test_sec_25_static_iv_or_hardcoded_salt(self) -> None:
        self._assert_triggers("SEC_25", 'salt = b"static_salt_value"\n')
        self._assert_clean("SEC_25", "import os\nsalt = os.urandom(16)\n")

    def test_sec_26_disabled_tls_certificate_verification(self) -> None:
        self._assert_triggers(
            "SEC_26",
            'import requests\nrequests.get("https://example.com", verify=False, timeout=5)\n',
        )
        self._assert_clean(
            "SEC_26",
            'import requests\nrequests.get("https://example.com", verify=True, timeout=5)\n',
        )

    def test_sec_27_weak_key_size_or_insecure_ssl(self) -> None:
        self._assert_triggers("SEC_27", "key = rsa.generate_private_key(key_size=1024)\n")
        self._assert_clean("SEC_27", "key = rsa.generate_private_key(key_size=2048)\n")

    # --- Category 5: Network & Server-Side Security (SEC_28 - SEC_33) ---

    def test_sec_28_ssrf_dynamic_url(self) -> None:
        self._assert_triggers("SEC_28", "import requests\nrequests.get(user_url, timeout=5)\n")
        self._assert_clean("SEC_28", 'import requests\nrequests.get("https://example.com", timeout=5)\n')

    def test_sec_29_unrestricted_socket_binding(self) -> None:
        self._assert_triggers("SEC_29", 'sock.bind(("0.0.0.0", 8080))\n')
        self._assert_clean("SEC_29", 'sock.bind(("127.0.0.1", 8080))\n')

    def test_sec_30_sensitive_data_exposure_in_logs(self) -> None:
        self._assert_triggers("SEC_30", "print(user_password)\n")
        self._assert_clean("SEC_30", "print(username)\n")

    def test_sec_31_cleartext_protocol_usage(self) -> None:
        self._assert_triggers("SEC_31", 'endpoint = "http://api.example.com/v1"\n')
        self._assert_clean("SEC_31", 'endpoint = "https://api.example.com/v1"\n')

    def test_sec_32_http_header_crlf_injection(self) -> None:
        self._assert_triggers("SEC_32", 'handler.send_header("X-User", user_input)\n')
        self._assert_clean("SEC_32", 'handler.send_header("Content-Type", "application/json")\n')

    def test_sec_33_debug_mode_or_open_redirect(self) -> None:
        self._assert_triggers("SEC_33", "app.run(debug=True)\n")
        self._assert_clean("SEC_33", "app.run(debug=False)\n")

    # --- Category 6: Denial of Service & Resource Control (SEC_34 - SEC_40) ---

    def test_sec_34_redos_nested_quantifier(self) -> None:
        self._assert_triggers("SEC_34", 'import re\np = re.compile(r"(a+)+$")\n')
        self._assert_clean("SEC_34", 'import re\np = re.compile(r"^[a-z0-9]+$")\n')

    def test_sec_35_unbounded_file_stream_read(self) -> None:
        self._assert_triggers("SEC_35", "content = fh.read()\n")
        self._assert_clean("SEC_35", "content = fh.read(4096)\n")

    def test_sec_36_unbounded_loop_hazard(self) -> None:
        self._assert_triggers("SEC_36", "while True:\n    x = 1\n")
        self._assert_clean("SEC_36", "while True:\n    break\n")

    def test_sec_37_unbounded_recursion_hazard(self) -> None:
        self._assert_triggers("SEC_37", "def loop(n):\n    return loop(n - 1)\n")
        self._assert_clean(
            "SEC_37",
            "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\n",
        )

    def test_sec_38_archive_decompression_bomb(self) -> None:
        self._assert_triggers("SEC_38", 'archive.extractall("/safe/dir")\n')
        self._assert_clean("SEC_38", 'archive.extract("single_file.txt", "/safe/dir")\n')

    def test_sec_39_missing_timeout(self) -> None:
        self._assert_triggers("SEC_39", 'import requests\nrequests.get("https://example.com")\n')
        self._assert_clean("SEC_39", 'import requests\nrequests.get("https://example.com", timeout=5)\n')

    def test_sec_40_unbounded_thread_spawning_in_loop(self) -> None:
        self._assert_triggers(
            "SEC_40",
            "import threading\nfor i in range(10):\n    threading.Thread(target=worker)\n",
        )
        self._assert_clean(
            "SEC_40",
            "import threading\nt = threading.Thread(target=worker)\n",
        )

    # --- Category 7: Low-Level / C++ Interop & Memory Safety (SEC_41 - SEC_45) ---

    def test_sec_41_buffer_overflow_unsafe_c_string(self) -> None:
        cpp_vuln = "int main() {\n    char dst[16];\n    strcpy(dst, src);\n    return 0;\n}\n"
        cpp_clean = "int main() {\n    int x = 42;\n    return x;\n}\n"
        self._assert_triggers("SEC_41", cpp_vuln, language="cpp")
        self._assert_clean("SEC_41", cpp_clean, language="cpp")

    def test_sec_42_use_after_free_and_raw_pointer_risk(self) -> None:
        # Python raw ctypes memory manipulation
        self._assert_triggers("SEC_42", "import ctypes\nctypes.memmove(dst, src, 16)\n")
        # C++ use-after-free
        cpp_uaf = "void run(int* ptr) {\n    free(ptr);\n    ptr[0] = 5;\n}\n"
        self._assert_triggers("SEC_42", cpp_uaf, language="cpp")
        self._assert_clean("SEC_42", "x = [1, 2, 3]\n")

    def test_sec_43_double_free_hazard(self) -> None:
        cpp_df = "void run(int* ptr) {\n    free(ptr);\n    free(ptr);\n}\n"
        cpp_clean = "void run(int* ptr) {\n    free(ptr);\n}\n"
        self._assert_triggers("SEC_43", cpp_df, language="cpp")
        self._assert_clean("SEC_43", cpp_clean, language="cpp")

    def test_sec_44_format_string_vulnerability(self) -> None:
        self._assert_triggers("SEC_44", 'msg = "{0}".format(**user_data)\n')
        cpp_fmt = "void log_msg(char* msg) {\n    printf(msg);\n}\n"
        self._assert_triggers("SEC_44", cpp_fmt, language="cpp")
        self._assert_clean("SEC_44", 'msg = "hello {}".format("world")\n')

    def test_sec_45_unchecked_allocation_or_bare_except_pass(self) -> None:
        self._assert_triggers("SEC_45", "try:\n    risky()\nexcept:\n    pass\n")
        cpp_malloc = "void alloc() {\n    void* p = malloc(128);\n}\n"
        self._assert_triggers("SEC_45", cpp_malloc, language="cpp")
        self._assert_clean("SEC_45", "try:\n    risky()\nexcept ValueError:\n    handle()\n")

    # --- Category 8: Quantitative Attack Surface & Complexity Metrics (SEC_46 - SEC_52) ---

    def test_sec_46_taint_flow_count(self) -> None:
        tainted = "import os\nuser_cmd = input('cmd: ')\nos.system(user_cmd)\n"
        rep_tainted = self.engine.analyze(tainted)
        self.assertGreaterEqual(rep_tainted["metrics"]["SEC_46"], 1)

        untainted = 'import os\nos.system("ls")\n'
        rep_untainted = self.engine.analyze(untainted)
        self.assertEqual(rep_untainted["metrics"]["SEC_46"], 0)

    def test_sec_47_dangerous_sink_density(self) -> None:
        # 2 calls total: os.system (dangerous sink) + len (safe) => 50.0%
        code = 'import os\nos.system("ls")\nn = len([1, 2, 3])\n'
        report = self.engine.analyze(code)
        self.assertAlmostEqual(report["metrics"]["SEC_47"], 50.0, places=2)

    def test_sec_48_security_cyclomatic_density(self) -> None:
        clean_rep = self.engine.analyze("x = 1\n")
        self.assertEqual(clean_rep["metrics"]["SEC_48"], 0.0)

        risky_rep = self.engine.analyze('import os\nos.system("ls")\n')
        expected = round(
            risky_rep["summary"]["raw_risk_score"] / max(1, risky_rep["summary"]["cyclomatic_complexity"]),
            4,
        )
        self.assertAlmostEqual(risky_rep["metrics"]["SEC_48"], expected, places=4)
        self.assertGreater(risky_rep["metrics"]["SEC_48"], 0.0)

    def test_sec_49_unsanitized_parameter_index(self) -> None:
        dyn = "import os\ncmd = 'ls'\nos.system(cmd)\n"
        lit = 'import os\nos.system("ls")\n'
        self.assertGreaterEqual(self.engine.analyze(dyn)["metrics"]["SEC_49"], 1)
        self.assertEqual(self.engine.analyze(lit)["metrics"]["SEC_49"], 0)

    def test_sec_50_privilege_exposure_score(self) -> None:
        # os (3.0) + subprocess (5.0) = 8.0
        code = "import os\nimport subprocess\n"
        report = self.engine.analyze(code)
        self.assertAlmostEqual(report["metrics"]["SEC_50"], 8.0, places=2)

    def test_sec_51_peak_string_secret_entropy(self) -> None:
        high_ent = 'token_val = "aB3$kL9!mN2@pQ7#rS5^tU8&wX0*"\n'
        low_ent = 'token_val = "aaaaaaaaaaaa"\n'
        self.assertGreater(self.engine.analyze(high_ent)["metrics"]["SEC_51"], 4.0)
        self.assertEqual(self.engine.analyze(low_ent)["metrics"]["SEC_51"], 0.0)

    def test_sec_52_overall_security_health_score(self) -> None:
        clean_rep = self.engine.analyze("def add(a, b):\n    return a + b\n")
        self.assertEqual(clean_rep["metrics"]["SEC_52"], 100.0)
        self.assertEqual(clean_rep["summary"]["grade"], "A")
        self.assertFalse(clean_rep["summary"]["blocked"])

        risky_rep = self.engine.analyze('import os\nos.system("rm -rf /")\n')
        raw_risk = risky_rep["summary"]["raw_risk_score"]
        expected_health = round(100.0 * math.exp(-raw_risk / 40.0), 2)
        self.assertAlmostEqual(risky_rep["metrics"]["SEC_52"], expected_health, places=2)
        self.assertLess(risky_rep["metrics"]["SEC_52"], 100.0)
        self.assertTrue(risky_rep["summary"]["blocked"])


class TestSecurityEngineAdvanced(unittest.TestCase):
    """Tests compare() zero-regression gate and syntax-error lexical fallback."""

    def setUp(self) -> None:
        self.engine = SecurityMetricsEngine()

    def test_compare_accepts_hardening_patch(self) -> None:
        before = 'import hashlib\nh = hashlib.md5(b"x")\n'
        after = 'import hashlib\nh = hashlib.sha256(b"x")\n'
        diff = self.engine.compare(before, after)
        self.assertTrue(diff["patch_safe"])
        self.assertIn("SEC_23", diff["resolved_metrics"])
        self.assertLess(diff["risk_delta"], 0)
        self.assertGreater(diff["health_delta"], 0)

    def test_compare_rejects_security_regression(self) -> None:
        before = "x = 1 + 1\n"
        after = 'import os\nos.system("id")\n'
        diff = self.engine.compare(before, after)
        self.assertFalse(diff["patch_safe"])
        self.assertIn("SEC_01", diff["introduced_severe_metrics"])

    def test_syntax_error_lexical_fallback_still_detects_sinks(self) -> None:
        broken = 'def f(:\n    import os\n    os.system("ls")\n    eval("1+1")\n'
        report = self.engine.analyze(broken)
        self.assertIsNotNone(report["summary"]["parse_error"])
        self.assertIn("SEC_01", report["triggered_metrics"])
        self.assertIn("SEC_02", report["triggered_metrics"])


if __name__ == "__main__":
    unittest.main()
