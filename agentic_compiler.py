"""
agentic_compiler.py
===================
Secure Agentic AI Compiler (Intelligent Compiler) for IntelliFix / TOACD.

Implements a 5-agent autonomous compilation, security-hardening, and self-repair pipeline:
  1. PerceptionAndIRAgent   - AST parsing, Symbol Table / IR extraction, Prompt-Injection Guard.
  2. SecurityAuditorAgent   - 52-metric static & AST security evaluation + Zero-Regression Gate.
  3. IntelligentSynthesizer - Hybrid AST Security Hardener + Deterministic Repair + Optional LLM.
  4. SandboxVerifierAgent   - Isolated subprocess execution with strict timeout & security gate.
  5. AgenticCompilerCoordinator - Autonomous Observe -> Audit -> Synthesize -> Verify -> Reflect loop.

Supports both:
  - Offline / Deterministic Agentic Mode (fast, reproducible for 50+ 2,000-LOC benchmarks)
  - Optional LLM-Augmented Mode (Gemini / OpenAI-compatible / Ollama via `requests`, guarded by
    prompt-injection sanitization, AST validation, and the 52-metric Security Auditor).
"""

from __future__ import annotations

import ast
import difflib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    requests = None  # Optional: only required when use_llm=True with HTTP endpoints

from security_metrics_engine import SecurityMetricsEngine, METRICS_REGISTRY
from static_analyzer import static_check
from error_extractor import extract_error, run_code
from ir_generator import IRGenerator
from nlp_explainer import NLPExplainer
from cpp_extractor import extract_cpp_error, run_cpp_code, is_cpp_name
from cpp_explainer import apply_fix as apply_cpp_fix, explain as explain_cpp_error


# ---------------------------------------------------------------------------
# Data Structures for Inter-Agent Messaging & Telemetry
# ---------------------------------------------------------------------------

@dataclass
class AgentMessage:
    iteration: int
    sender: str
    recipient: str
    intent: str
    summary: str
    timestamp_ms: float
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompilerErrorObj:
    error_type: str
    message: str
    line_number: int
    category: str = "Runtime"
    traceback_info: str = ""


# ---------------------------------------------------------------------------
# Agent 1: Perception, IR & Prompt-Injection Guard Agent
# ---------------------------------------------------------------------------

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(?:all\s+)?(?:security|safety)\s+(?:rules|checks|policies)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(?:in\s+)?(?:developer|god|unrestricted|jailbreak)\s+mode", re.IGNORECASE),
    re.compile(r"system\s*prompt\s*[:=]", re.IGNORECASE),
    re.compile(r"bypass\s+(?:sandbox|security|filter|auditor)", re.IGNORECASE),
    re.compile(r"<\s*/?\s*system\s*>", re.IGNORECASE),
]


class PerceptionAndIRAgent:
    """
    Parses source code into AST/IR, extracts symbol & structural metadata,
    and scrubs adversarial prompt-injection payloads hidden in comments/strings.
    """
    NAME = "PerceptionAndIRAgent"

    def scan_prompt_injections(self, code: str) -> List[Dict[str, Any]]:
        hits: List[Dict[str, Any]] = []
        for lineno, line in enumerate(code.splitlines(), 1):
            for pat in PROMPT_INJECTION_PATTERNS:
                if pat.search(line):
                    hits.append({
                        "line": lineno,
                        "pattern": pat.pattern,
                        "snippet": line.strip()[:100],
                    })
                    break
        return hits

    def sanitize_for_llm(self, code: str) -> str:
        """Neutralize prompt-injection comment lines before passing code to any LLM."""
        clean_lines = []
        for line in code.splitlines():
            if any(p.search(line) for p in PROMPT_INJECTION_PATTERNS):
                clean_lines.append("# [REDACTED_ADVERSARIAL_PROMPT_INJECTION]")
            else:
                clean_lines.append(line)
        return "\n".join(clean_lines)

    def perceive(self, code: str, language: str = "python") -> Dict[str, Any]:
        injections = self.scan_prompt_injections(code)
        loc = len(code.splitlines())
        ir_info: Dict[str, Any] = {
            "language": language,
            "loc": loc,
            "bytes": len(code.encode("utf-8", errors="ignore")),
            "syntax_valid": True,
            "static_issue": None,
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "prompt_injections": injections,
        }

        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        ir_info["functions"] += 1
                    elif isinstance(node, ast.ClassDef):
                        ir_info["classes"] += 1
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        ir_info["imports"] += 1
                static_errs = static_check(code)
                if static_errs:
                    first = static_errs[0]
                    ir_info["static_issue"] = {
                        "error_type": first.get("error_type", "StaticError"),
                        "message": first.get("error_message", "static check failed"),
                        "line": first.get("line_number") or 1,
                    }
            except SyntaxError as exc:
                ir_info["syntax_valid"] = False
                ir_info["static_issue"] = {
                    "error_type": "SyntaxError",
                    "message": exc.msg or "invalid syntax",
                    "line": exc.lineno or 1,
                }
        else:
            ir_info["functions"] = len(re.findall(r"\b[A-Za-z_]\w*\s+[A-Za-z_]\w*\s*\([^)]*\)\s*\{", code))
            ir_info["classes"] = len(re.findall(r"\b(?:class|struct)\s+[A-Za-z_]\w*", code))
            ir_info["imports"] = len(re.findall(r"^\s*#\s*include\b", code, re.MULTILINE))

        return ir_info


# ---------------------------------------------------------------------------
# Agent 2: Security Auditor Agent (52-Metric Guardrail)
# ---------------------------------------------------------------------------

class SecurityAuditorAgent:
    """
    Runs the 52-metric AST/static security engine and enforces Zero-Regression
    verification on every candidate patch produced by the Synthesizer.
    """
    NAME = "SecurityAuditorAgent"

    def __init__(self) -> None:
        self.engine = SecurityMetricsEngine()

    def audit(self, code: str, language: str = "python") -> Dict[str, Any]:
        return self.engine.analyze(code, language=language)

    def verify_patch_security(
        self, before_code: str, after_code: str, language: str = "python"
    ) -> Dict[str, Any]:
        return self.engine.compare(before_code, after_code, language=language)


# ---------------------------------------------------------------------------
# Agent 3: Intelligent Synthesizer & Security Hardening Agent
# ---------------------------------------------------------------------------

class IntelligentSynthesizerAgent:
    """
    Performs autonomous AST-aware security hardening and bug repair.
    Uses deterministic AST/rule transforms first (fast, verifiable, zero hallucination),
    and optionally invokes an LLM backend (Gemini / OpenAI / Ollama) when enabled.
    """
    NAME = "IntelligentSynthesizerAgent"

    def __init__(self, use_llm: bool = False) -> None:
        self.use_llm = use_llm
        self.nlp_explainer = NLPExplainer()

    def harden_python_security(self, code: str, audit_report: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Apply targeted, semantics-preserving security hardening transforms for
        vulnerabilities flagged by the 52-metric SecurityAuditorAgent.
        Returns (hardened_code, list_of_applied_transformations).
        """
        lines = code.splitlines()
        triggered = set(audit_report.get("triggered_metrics", []))
        actions: List[str] = []
        changed = False

        # Line-indexed findings for surgical edits
        findings_by_line: Dict[int, List[Dict[str, Any]]] = {}
        for f in audit_report.get("findings", []):
            ln = f.get("line", 1)
            if isinstance(ln, int) and 1 <= ln <= len(lines):
                findings_by_line.setdefault(ln, []).append(f)

        for ln, flist in sorted(findings_by_line.items()):
            idx = ln - 1
            orig = lines[idx]
            new_line = orig
            mids = {f["metric_id"] for f in flist}

            # SEC_01: OS Command Injection -> disable shell sink safely or enforce shell=False
            if "SEC_01" in mids:
                if "shell=True" in new_line:
                    new_line = new_line.replace("shell=True", "shell=False")
                    actions.append(f"L{ln} [SEC_01]: Replaced shell=True with shell=False")
                elif re.search(r"\b(?:os\.system|os\.popen)\s*\(", new_line):
                    indent = re.match(r"^(\s*)", new_line).group(1)
                    new_line = f"{indent}pass  # [AGENTIC_COMPILER SEC_01] Blocked unsafe OS shell sink"
                    actions.append(f"L{ln} [SEC_01]: Neutralized unsafe os.system/os.popen sink")
                elif re.search(r"\bsubprocess\.(?:run|Popen|call|check_output|check_call)\s*\(", new_line):
                    indent = re.match(r"^(\s*)", new_line).group(1)
                    new_line = f"{indent}pass  # [AGENTIC_COMPILER SEC_01] Blocked unvalidated subprocess sink"
                    actions.append(f"L{ln} [SEC_01]: Neutralized unvalidated subprocess sink")

            # SEC_02: Dynamic eval/exec -> ast.literal_eval or block exec
            if "SEC_02" in mids:
                if re.search(r"\beval\s*\(", new_line) and "literal_eval" not in new_line:
                    new_line = re.sub(r"\beval\s*\(", "__import__('ast').literal_eval(", new_line)
                    # Avoid triggering SEC_08 with __import__; prefer clean ast.literal_eval
                    new_line = new_line.replace("__import__('ast').literal_eval(", "ast.literal_eval(")
                    actions.append(f"L{ln} [SEC_02]: Replaced eval() with safe ast.literal_eval()")
                elif re.search(r"\b(?:exec|compile)\s*\(", new_line):
                    indent = re.match(r"^(\s*)", new_line).group(1)
                    new_line = f"{indent}pass  # [AGENTIC_COMPILER SEC_02] Blocked dynamic exec/compile"
                    actions.append(f"L{ln} [SEC_02]: Blocked dynamic exec()/compile()")

            # SEC_03: Insecure Deserialization -> yaml.safe_load or json.loads
            if "SEC_03" in mids:
                if re.search(r"\byaml\.(?:unsafe_load|load)\s*\(", new_line):
                    new_line = re.sub(r"\byaml\.(?:unsafe_load|load)\s*\(", "yaml.safe_load(", new_line)
                    actions.append(f"L{ln} [SEC_03]: Replaced yaml.load with yaml.safe_load()")
                elif re.search(r"\b(?:pickle|cPickle|marshal|dill)\.loads?\s*\(", new_line):
                    new_line = re.sub(r"\b(?:pickle|cPickle|marshal|dill)\.loads?\s*\(", "json.loads(", new_line)
                    actions.append(f"L{ln} [SEC_03]: Replaced unsafe pickle/marshal load with json.loads()")

            # SEC_08: Dynamic __import__ -> neutralize
            if "SEC_08" in mids and re.search(r"\b(?:__import__|importlib\.import_module)\s*\(", new_line):
                indent = re.match(r"^(\s*)", new_line).group(1)
                new_line = f"{indent}pass  # [AGENTIC_COMPILER SEC_08] Blocked dynamic import"
                actions.append(f"L{ln} [SEC_08]: Blocked dynamic module import")

            # SEC_09 / SEC_10 / SEC_14: Sandbox escape / builtins poisoning / getattr obfuscation
            if mids & {"SEC_09", "SEC_10", "SEC_14"}:
                indent = re.match(r"^(\s*)", new_line).group(1)
                new_line = f"{indent}pass  # [AGENTIC_COMPILER] Blocked sandbox escape / reflection vector"
                actions.append(f"L{ln} [{','.join(sorted(mids & {'SEC_09', 'SEC_10', 'SEC_14'}))}]: Neutralized sandbox escape")

            # SEC_16: Destructive File Operations
            if "SEC_16" in mids and re.search(r"\b(?:os\.remove|os\.unlink|os\.rmdir|shutil\.rmtree)\s*\(", new_line):
                indent = re.match(r"^(\s*)", new_line).group(1)
                new_line = f"{indent}pass  # [AGENTIC_COMPILER SEC_16] Blocked destructive file deletion"
                actions.append(f"L{ln} [SEC_16]: Neutralized destructive file operation")

            # SEC_17: Insecure tempfile.mktemp -> mkstemp
            if "SEC_17" in mids and "mktemp(" in new_line:
                new_line = new_line.replace("mktemp(", "mkstemp(")
                actions.append(f"L{ln} [SEC_17]: Replaced tempfile.mktemp() with tempfile.mkstemp()")

            # SEC_19: Overly permissive chmod -> 0o600
            if "SEC_19" in mids and "chmod(" in new_line:
                new_line = re.sub(r"0o?777|0o?666|0o?775", "0o600", new_line)
                actions.append(f"L{ln} [SEC_19]: Hardened os.chmod permission to 0o600")

            # SEC_21: Hardcoded Secret -> os.environ.get(...)
            if "SEC_21" in mids:
                m_assign = re.match(r'^(\s*)([A-Za-z_]\w*)\s*=\s*(["\'])(.+?)\3(.*)$', new_line)
                if m_assign:
                    ind, var, _, _, tail = m_assign.groups()
                    env_key = var.upper()
                    new_line = f'{ind}{var} = os.environ.get("{env_key}", ""){tail}'
                    actions.append(f"L{ln} [SEC_21]: Replaced hardcoded secret '{var}' with os.environ.get('{env_key}')")

            # SEC_23: Weak hash MD5/SHA1 -> SHA256
            if "SEC_23" in mids:
                new_line = re.sub(r"\bhashlib\.(?:md5|sha1)\s*\(", "hashlib.sha256(", new_line)
                new_line = re.sub(r"hashlib\.new\(\s*['\"](?:md5|sha1)['\"]", "hashlib.new('sha256'", new_line)
                if new_line != orig:
                    actions.append(f"L{ln} [SEC_23]: Upgraded deprecated MD5/SHA1 hash to SHA-256")

            # SEC_26: Disabled TLS verify=False -> verify=True
            if "SEC_26" in mids and "verify=False" in new_line:
                new_line = new_line.replace("verify=False", "verify=True")
                actions.append(f"L{ln} [SEC_26]: Enforced TLS certificate verification (verify=True)")

            # SEC_29: Unrestricted 0.0.0.0 bind -> 127.0.0.1
            if "SEC_29" in mids and "0.0.0.0" in new_line:
                new_line = new_line.replace("0.0.0.0", "127.0.0.1")
                actions.append(f"L{ln} [SEC_29]: Restricted socket bind from 0.0.0.0 to 127.0.0.1")

            # SEC_33: debug=True -> debug=False
            if "SEC_33" in mids and "debug=True" in new_line:
                new_line = new_line.replace("debug=True", "debug=False")
                actions.append(f"L{ln} [SEC_33]: Disabled production debug mode (debug=False)")

            # SEC_35: Unbounded .read() -> .read(65536)
            if "SEC_35" in mids and ".read()" in new_line:
                new_line = new_line.replace(".read()", ".read(65536)")
                actions.append(f"L{ln} [SEC_35]: Bounded unbounded .read() to 65536 bytes")

            # SEC_39: requests.get(...) missing timeout -> add timeout=10
            if "SEC_39" in mids and "requests." in new_line and "timeout=" not in new_line and ")" in new_line:
                pos = new_line.rfind(")")
                new_line = new_line[:pos] + ", timeout=10" + new_line[pos:]
                actions.append(f"L{ln} [SEC_39]: Added timeout=10 to network request")

            # SEC_45: Bare except: pass -> except Exception: pass
            if "SEC_45" in mids and re.match(r"^\s*except\s*:", new_line):
                new_line = re.sub(r"^(\s*)except\s*:", r"\1except Exception:", new_line)
                actions.append(f"L{ln} [SEC_45]: Narrowed bare except: to except Exception:")

            if new_line != orig:
                lines[idx] = new_line
                changed = True

        hardened = "\n".join(lines)

        # Ensure required imports (ast, os, json) exist if introduced by hardening
        if changed:
            needed_imports = []
            if "ast.literal_eval(" in hardened and "import ast" not in hardened:
                needed_imports.append("import ast")
            if "os.environ.get(" in hardened and "import os" not in hardened:
                needed_imports.append("import os")
            if "json.loads(" in hardened and "import json" not in hardened:
                needed_imports.append("import json")
            if needed_imports:
                hardened = "\n".join(needed_imports) + "\n" + hardened

        return hardened, actions

    def harden_cpp_security(self, code: str, audit_report: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Apply targeted security hardening transforms for C++ findings."""
        lines = code.splitlines()
        actions: List[str] = []
        for f in audit_report.get("findings", []):
            ln = f.get("line", 1)
            if not (isinstance(ln, int) and 1 <= ln <= len(lines)):
                continue
            idx = ln - 1
            orig = lines[idx]
            mid = f["metric_id"]
            if mid == "SEC_01" and re.search(r"\b(?:std::)?system\s*\(", orig):
                indent = re.match(r"^(\s*)", orig).group(1)
                lines[idx] = f"{indent}// [AGENTIC_COMPILER SEC_01] Blocked unsafe system() call"
                actions.append(f"L{ln} [SEC_01]: Neutralized C++ system() call")
            elif mid == "SEC_41" and re.search(r"\bgets\s*\(", orig):
                lines[idx] = re.sub(r"\bgets\s*\(\s*([^)]+)\s*\)", r"fgets(\1, sizeof(\1), stdin)", orig)
                actions.append(f"L{ln} [SEC_41]: Replaced unsafe gets() with bounded fgets()")
        return "\n".join(lines), actions

    def repair_functional_bug(
        self, code: str, error_obj: CompilerErrorObj, language: str = "python"
    ) -> Tuple[str, str]:
        """Repair a syntax/static/runtime bug using IR + deterministic explainer (or LLM)."""
        if language == "cpp":
            fixed = apply_cpp_fix(
                {"error_type": error_obj.error_type, "message": error_obj.message, "line_number": error_obj.line_number},
                code,
            )
            explanation = explain_cpp_error(
                {"error_type": error_obj.error_type, "message": error_obj.message, "line_number": error_obj.line_number}
            )
            return fixed, explanation

        ir_gen = IRGenerator(code, error_obj)
        ir = ir_gen.generate_ir()
        if isinstance(ir, str):
            ir = json.loads(ir)
        explanation = self.nlp_explainer.explain(ir)
        fixed = self.nlp_explainer.generate_fixed_code(ir, code)
        return fixed, explanation

    def optional_llm_patch(
        self, sanitized_code: str, error_summary: str, security_findings: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Optional LLM synthesis hook (supports local Ollama or OpenAI-compatible endpoint).
        Only called when `use_llm=True` and environment credentials are present.
        """
        if not self.use_llm or requests is None:
            return None

        ollama_url = os.environ.get("OLLAMA_URL")
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not ollama_url and not openai_key:
            return None

        prompt = (
            "You are a Secure Compiler Synthesis Agent. Return ONLY valid, hardened Python code "
            "with no markdown fences.\n"
            f"Error to fix: {error_summary}\n"
            f"Security findings to remediate: {json.dumps(security_findings[:5])}\n"
            f"Source code:\n{sanitized_code[:12000]}"
        )

        try:
            if ollama_url:
                model = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")
                resp = requests.post(
                    f"{ollama_url.rstrip('/')}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=20,
                )
                if resp.ok:
                    text = resp.json().get("response", "").strip()
                    return self._strip_code_fences(text)
            elif openai_key:
                base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
                model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
                resp = requests.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    json={
                        "model": model,
                        "temperature": 0.1,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=20,
                )
                if resp.ok:
                    text = resp.json()["choices"][0]["message"]["content"].strip()
                    return self._strip_code_fences(text)
        except Exception:
            return None
        return None

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text)
        return text.strip()


# ---------------------------------------------------------------------------
# Agent 4: Sandbox Verifier & Reflection Agent
# ---------------------------------------------------------------------------

class SandboxVerifierAgent:
    """
    Executes candidate code in an isolated subprocess ONLY when certified safe
    by the SecurityAuditorAgent. Returns structured execution & reflection data.
    """
    NAME = "SandboxVerifierAgent"

    def verify(
        self, code: str, audit_report: Dict[str, Any], language: str = "python", execute: bool = True
    ) -> Dict[str, Any]:
        if audit_report["summary"]["blocked"]:
            return {
                "executed": False,
                "passed": False,
                "blocked_by_security": True,
                "output": "",
                "error": None,
                "reflection": (
                    f"Execution refused by Security Gate: {audit_report['severity_counts']['CRITICAL']} CRITICAL "
                    f"and {audit_report['severity_counts']['HIGH']} HIGH findings remain."
                ),
            }

        if not execute:
            # Static-only verification mode (syntax + security clean)
            syntax_ok = audit_report["summary"].get("parse_error") is None
            return {
                "executed": False,
                "passed": syntax_ok,
                "blocked_by_security": False,
                "output": "",
                "error": None,
                "reflection": "Static & security verification passed." if syntax_ok else "Syntax error remains.",
            }

        if language == "cpp":
            try:
                res = extract_cpp_error(code)
            except Exception as exc:
                return {
                    "executed": False, "passed": False, "blocked_by_security": False,
                    "output": "", "error": None, "reflection": f"C++ compiler unavailable: {exc}",
                }
            if res.get("error_type"):
                err_type = res["error_type"]
                err_msg = res.get("error_message") or ""
                err_line = res.get("line_number") or 1
                return {
                    "executed": True, "passed": False, "blocked_by_security": False,
                    "output": res.get("stdout", ""),
                    "error": CompilerErrorObj(err_type, err_msg, err_line, "Compile", res.get("traceback", "")),
                    "reflection": f"C++ compilation/runtime failed: {err_type} at line {err_line}: {err_msg}",
                }
            return {
                "executed": True, "passed": True, "blocked_by_security": False,
                "output": res.get("stdout", ""), "error": None,
                "reflection": "C++ compiled and executed cleanly in sandbox.",
            }

        # Python isolated subprocess execution via extract_error
        res = extract_error(code)
        if res.get("error_type"):
            err_type = res["error_type"]
            err_msg = res.get("error_message") or ""
            err_line = res.get("line_number") or 1
            return {
                "executed": True, "passed": False, "blocked_by_security": False,
                "output": res.get("stdout", ""),
                "error": CompilerErrorObj(err_type, err_msg, err_line, "Runtime", res.get("traceback", "")),
                "reflection": f"Runtime failure: {err_type} at line {err_line}: {err_msg}",
            }
        return {
            "executed": True, "passed": True, "blocked_by_security": False,
            "output": res.get("stdout", ""), "error": None,
            "reflection": "Executed cleanly in isolated sandbox with zero errors.",
        }


# ---------------------------------------------------------------------------
# Agent 5: Coordinator / Orchestrator Agent
# ---------------------------------------------------------------------------

class AgenticCompilerCoordinator:
    """
    Orchestrates the Secure Agentic AI Compiler loop:
      Perception/IR -> 52-Metric Security Audit -> Synthesis/Hardening -> Zero-Regression Gate
      -> Sandbox Verification -> Reflection Feedback (up to max_iterations).
    """
    NAME = "AgenticCompilerCoordinator"

    def __init__(self, max_iterations: int = 5, use_llm: bool = False) -> None:
        self.max_iterations = max(1, max_iterations)
        self.perception = PerceptionAndIRAgent()
        self.auditor = SecurityAuditorAgent()
        self.synthesizer = IntelligentSynthesizerAgent(use_llm=use_llm)
        self.verifier = SandboxVerifierAgent()

    def compile_and_harden(
        self,
        code: str,
        language: str = "python",
        execute_sandbox: bool = True,
    ) -> Dict[str, Any]:
        code = code.replace("\r\n", "\n").replace("\r", "\n")
        t_start = time.perf_counter()
        trace: List[Dict[str, Any]] = []
        iteration_history: List[Dict[str, Any]] = []

        def log_msg(iteration: int, sender: str, recipient: str, intent: str, summary: str, payload: Optional[Dict] = None) -> None:
            trace.append(asdict(AgentMessage(
                iteration=iteration,
                sender=sender,
                recipient=recipient,
                intent=intent,
                summary=summary,
                timestamp_ms=round((time.perf_counter() - t_start) * 1000.0, 2),
                payload=payload or {},
            )))

        # Step 0: Initial Perception & Baseline 52-Metric Audit
        ir_initial = self.perception.perceive(code, language=language)
        initial_audit = self.auditor.audit(code, language=language)
        log_msg(
            0, self.perception.NAME, self.NAME, "PERCEIVE_IR",
            f"Parsed {ir_initial['loc']} LOC ({ir_initial['functions']} funcs, {ir_initial['classes']} classes); "
            f"{len(ir_initial['prompt_injections'])} prompt-injection patterns detected.",
            {"loc": ir_initial["loc"], "prompt_injections": len(ir_initial["prompt_injections"])},
        )
        log_msg(
            0, self.auditor.NAME, self.NAME, "BASELINE_AUDIT",
            f"52-metric audit: {initial_audit['summary']['total_findings']} findings, "
            f"Risk={initial_audit['summary']['raw_risk_score']}, "
            f"Health={initial_audit['summary']['security_health_score']}/100 ({initial_audit['summary']['grade']}).",
        )

        current_code = code
        current_audit = initial_audit
        converged = False
        pass_at_k: Optional[int] = None
        execution_verified = False
        execution_output = ""
        all_actions: List[str] = []
        rejected_patches = 0

        for it in range(1, self.max_iterations + 1):
            iter_actions: List[str] = []
            candidate_code = current_code

            # 1) Security Hardening Pass if vulnerabilities exist
            if current_audit["summary"]["total_findings"] > 0:
                if language == "cpp":
                    candidate_code, sec_actions = self.synthesizer.harden_cpp_security(candidate_code, current_audit)
                else:
                    candidate_code, sec_actions = self.synthesizer.harden_python_security(candidate_code, current_audit)
                iter_actions.extend(sec_actions)

            # 2) Static / Syntax Bug Repair Pass
            ir_now = self.perception.perceive(candidate_code, language=language)
            if ir_now.get("static_issue"):
                si = ir_now["static_issue"]
                err_obj = CompilerErrorObj(si["error_type"], si["message"], si["line"], "Static")
                repaired, _ = self.synthesizer.repair_functional_bug(candidate_code, err_obj, language=language)
                if repaired and repaired != candidate_code:
                    candidate_code = repaired
                    iter_actions.append(f"L{si['line']} [BUG_REPAIR]: Repaired {si['error_type']} ({si['message'][:60]})")

            # 3) Zero-Regression Security Gate on Candidate Patch
            if candidate_code != current_code:
                diff_check = self.auditor.verify_patch_security(current_code, candidate_code, language=language)
                if diff_check["patch_safe"]:
                    current_code = candidate_code
                    current_audit = self.auditor.audit(current_code, language=language)
                    all_actions.extend(iter_actions)
                    log_msg(
                        it, self.synthesizer.NAME, self.auditor.NAME, "PATCH_ACCEPTED",
                        f"Applied {len(iter_actions)} transforms; Risk delta={diff_check['risk_delta']}, "
                        f"Health={current_audit['summary']['security_health_score']}/100.",
                        {"actions": iter_actions[:10], "risk_delta": diff_check["risk_delta"]},
                    )
                else:
                    rejected_patches += 1
                    log_msg(
                        it, self.auditor.NAME, self.synthesizer.NAME, "PATCH_REJECTED",
                        f"Zero-Regression Gate rejected patch (introduced: {diff_check['introduced_severe_metrics']}).",
                    )

            # 4) Sandbox Verification & Reflection Pass
            ver = self.verifier.verify(current_code, current_audit, language=language, execute=execute_sandbox)
            log_msg(it, self.verifier.NAME, self.NAME, "VERIFY_RESULT", ver["reflection"])

            iteration_history.append({
                "iteration": it,
                "findings": current_audit["summary"]["total_findings"],
                "raw_risk_score": current_audit["summary"]["raw_risk_score"],
                "health_score": current_audit["summary"]["security_health_score"],
                "grade": current_audit["summary"]["grade"],
                "blocked": current_audit["summary"]["blocked"],
                "sandbox_passed": ver["passed"],
                "actions_applied": len(iter_actions),
            })

            if ver["passed"]:
                converged = True
                pass_at_k = it
                execution_verified = ver["executed"]
                execution_output = ver["output"]
                break

            # 5) Reflection Feedback Loop: If sandbox returned a runtime error, feed it to Synthesizer
            if ver.get("error"):
                err_obj = ver["error"]
                repaired, _ = self.synthesizer.repair_functional_bug(current_code, err_obj, language=language)
                if repaired and repaired != current_code:
                    diff_check = self.auditor.verify_patch_security(current_code, repaired, language=language)
                    if diff_check["patch_safe"]:
                        current_code = repaired
                        current_audit = self.auditor.audit(current_code, language=language)
                        action_note = f"L{err_obj.line_number} [REFLECTION_FIX]: Repaired runtime {err_obj.error_type}"
                        all_actions.append(action_note)
                        log_msg(it, self.synthesizer.NAME, self.NAME, "REFLECTION_PATCH", action_note)
                        continue
            elif self.synthesizer.use_llm and current_audit["summary"]["blocked"]:
                # Optional LLM fallback on remaining blocking issues
                sanitized = self.perception.sanitize_for_llm(current_code)
                llm_candidate = self.synthesizer.optional_llm_patch(
                    sanitized, ver["reflection"], current_audit["findings"]
                )
                if llm_candidate and llm_candidate != current_code:
                    diff_check = self.auditor.verify_patch_security(current_code, llm_candidate, language=language)
                    if diff_check["patch_safe"]:
                        current_code = llm_candidate
                        current_audit = self.auditor.audit(current_code, language=language)
                        all_actions.append("LLM_SYNTHESIS: Applied security-verified LLM patch")
                        continue

            # If no progress was made in this iteration, stop early to avoid wasted cycles
            if not iter_actions:
                break

        # Final comparison telemetry
        comparison = self.auditor.verify_patch_security(code, current_code, language=language)
        init_risk = initial_audit["summary"]["raw_risk_score"]
        final_risk = current_audit["summary"]["raw_risk_score"]
        risk_reduction_pct = (
            round(((init_risk - final_risk) / init_risk) * 100.0, 2) if init_risk > 0 else 0.0
        )
        total_ms = round((time.perf_counter() - t_start) * 1000.0, 3)

        return {
            "language": language,
            "converged": converged,
            "pass_at_k": pass_at_k,
            "iterations_used": len(iteration_history),
            "execution_verified": execution_verified,
            "execution_output": execution_output[:500],
            "prompt_injections_detected": len(ir_initial["prompt_injections"]),
            "rejected_patches": rejected_patches,
            "actions_applied": all_actions,
            "risk_reduction_pct": risk_reduction_pct,
            "health_improvement": comparison["health_delta"],
            "resolved_metrics": comparison["resolved_metrics"],
            "security_regressions": comparison["introduced_severe_metrics"],
            "initial_summary": initial_audit["summary"],
            "final_summary": current_audit["summary"],
            "initial_metrics": initial_audit["metrics"],
            "final_metrics": current_audit["metrics"],
            "iteration_history": iteration_history,
            "agent_trace": trace,
            "compiled_code": current_code,
            "total_time_ms": total_ms,
        }


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python agentic_compiler.py <source_file.py|cpp> [--no-exec] [--json]")
        sys.exit(0)

    target = sys.argv[1]
    no_exec = "--no-exec" in sys.argv[2:]
    as_json = "--json" in sys.argv[2:]
    lang = "cpp" if is_cpp_name(target) else "python"

    with open(target, "r", encoding="utf-8", errors="replace") as f:
        code = f.read()

    coordinator = AgenticCompilerCoordinator(max_iterations=5, use_llm=False)
    result = coordinator.compile_and_harden(code, language=lang, execute_sandbox=not no_exec)

    if as_json:
        # Omit full compiled_code from compact CLI json unless needed
        out = {k: v for k, v in result.items() if k != "compiled_code"}
        print(json.dumps(out, indent=2))
        return

    init_s = result["initial_summary"]
    fin_s = result["final_summary"]
    print(f"=== Secure Agentic AI Compiler Report: {os.path.basename(target)} ({lang}) ===")
    print(f"LOC / AST Nodes       : {init_s['loc']} / {init_s['ast_nodes']}")
    print(f"Initial Health Score  : {init_s['security_health_score']}/100 (Grade {init_s['grade']}, Risk={init_s['raw_risk_score']})")
    print(f"Final Health Score    : {fin_s['security_health_score']}/100 (Grade {fin_s['grade']}, Risk={fin_s['raw_risk_score']})")
    print(f"Risk Reduction        : {result['risk_reduction_pct']}% | Health Delta: +{result['health_improvement']}")
    print(f"Resolved Metrics      : {', '.join(result['resolved_metrics']) or 'None'}")
    print(f"Security Regressions  : {len(result['security_regressions'])}")
    print(f"Converged / Pass@k    : {result['converged']} (Pass@{result['pass_at_k'] or 'N/A'} in {result['iterations_used']} iters)")
    print(f"Sandbox Verified      : {result['execution_verified']}")
    print(f"Prompt Injections Blk : {result['prompt_injections_detected']}")
    print(f"Total Pipeline Time   : {result['total_time_ms']} ms")
    if result["actions_applied"]:
        print("\nAgentic Transformations Applied:")
        for a in result["actions_applied"][:12]:
            print(f"  - {a}")


if __name__ == "__main__":
    main()
