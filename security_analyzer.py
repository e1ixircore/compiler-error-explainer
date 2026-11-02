import ast

# Dotted-name blocklist. Resolving the full name (os.system, not just .system)
# means we catch subprocess.run etc. without flagging every method named run().
DANGEROUS = {
    "os.system": ("Command Injection", "CRITICAL"),
    "os.popen": ("Command Injection", "CRITICAL"),
    "subprocess.run": ("Command Injection", "CRITICAL"),
    "subprocess.Popen": ("Command Injection", "CRITICAL"),
    "subprocess.call": ("Command Injection", "CRITICAL"),
    "subprocess.check_output": ("Command Injection", "CRITICAL"),
    "eval": ("Arbitrary Code Execution", "HIGH"),
    "exec": ("Arbitrary Code Execution", "HIGH"),
    "__import__": ("Arbitrary Code Execution", "HIGH"),
    "shutil.rmtree": ("Destructive File Operation", "HIGH"),
}

def _dotted(node):
    """ast.Attribute chain -> 'os.path.join'; None if the base isn't a plain name."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        return f"{base}.{node.attr}" if base else None
    return None

class SecurityAnalyzer:
    def __init__(self):
        """
        Week 10: Security Enforcement Mechanism
        Implements static analysis using Python's AST to detect 4 major vulnerabilities:
        1. Command Injection (e.g., os.system)
        2. Arbitrary Code Execution (e.g., eval, exec)
        3. Insecure Temporary Files (e.g., tempfile.mktemp)
        4. Hardcoded Secrets (e.g., variables named 'password', 'secret', 'apikey')
        """
        pass

    def scan_code(self, code_string):
        """
        Parses the code string and returns a list of detected vulnerabilities.
        """
        vulnerabilities = []
        try:
            tree = ast.parse(code_string)
        except SyntaxError:
            return vulnerabilities          # let the sandbox report it with a line number
        except (RecursionError, MemoryError, ValueError):
            # Hostile/pathological input: refuse it instead of crashing the compiler.
            return [{"type": "Unanalyzable Input", "severity": "HIGH",
                     "message": "Input too deeply nested or malformed to analyze safely.",
                     "line": 1}]

        for node in ast.walk(tree):
        
            # Vulnerability 1: Insecure Temporary Files
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == 'mktemp':
                    vulnerabilities.append({
                        "type": "Insecure Temp File",
                        "severity": "MEDIUM",
                        "message": "mktemp() is insecure. Use tempfile.mkstemp() instead.",
                        "line": getattr(node, 'lineno', 'Unknown')
                    })

            # Vulnerability 2: Hardcoded Secrets
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        if any(secret in var_name for secret in ['password', 'secret', 'api_key', 'token']):
                            vulnerabilities.append({
                                "type": "Hardcoded Secret",
                                "severity": "LOW",
                                "message": f"Potential hardcoded secret detected in variable '{target.id}'.",
                                "line": getattr(target, 'lineno', 'Unknown')
                            })

            # Calls: look up the dotted name in the blocklist
            if isinstance(node, ast.Call):
                name = _dotted(node.func)
                if name in DANGEROUS:
                    t, sev = DANGEROUS[name]
                    vulnerabilities.append({"type": t, "severity": sev,
                        "message": f"{name}() detected.", "line": node.lineno})

            # `from os import system` hides the module from the call site
            if isinstance(node, ast.ImportFrom) and node.module in ("os", "subprocess"):
                for a in node.names:
                    if f"{node.module}.{a.name}" in DANGEROUS:
                        vulnerabilities.append({"type": "Command Injection", "severity": "CRITICAL",
                            "message": f"from {node.module} import {a.name} bypasses call-site checks.",
                            "line": node.lineno})

        return vulnerabilities
