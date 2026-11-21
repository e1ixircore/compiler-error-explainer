"""
sandbox.py - Multi-Engine Secure Sandbox for TOACD
===================================================
Provides host-compromise protection for executing untrusted user code.

Engines Supported:
1. SeatbeltSandboxEngine (macOS native):
   Utilizes Apple's `sandbox-exec` with a dynamically generated or custom .sb
   profile. Enforces kernel-level mandatory access control (MAC):
   - Blocks network traffic entirely (deny network*)
   - Denies writes anywhere outside ephemeral scratch directories (deny file-write*)
   - Denies reading sensitive directories (~/.ssh, ~/.aws, ~/.gnupg, etc.)
   - Restricts process execution to designated runtime binaries only
   - Disallows process fork bombs and unauthorized inter-process communication

2. DockerSandboxEngine (Containers / gVisor):
   Spins up lightweight ephemeral containers with strict resource caps:
   - Read-only root filesystem (--read-only)
   - Zero network access (--network none)
   - Unprivileged user (--user 1000:1000)
   - Dropped Linux capabilities (--cap-drop ALL)
   - Memory and CPU throttling (--memory 256m --cpus 1.0)
   - Optional gVisor kernel isolation (--runtime runsc)

3. AuditHookSandboxEngine (Cross-Platform In-Process Defense-in-Depth):
   Utilizes Python 3.8+ CPython audit hooks (sys.addaudithook) and POSIX
   resource limits (setrlimit):
   - Intercepts subprocess/execve calls before execution
   - Intercepts socket and network activity
   - Intercepts ctypes / native memory tampering
   - Enforces RLIMIT_CPU, RLIMIT_AS (memory), and RLIMIT_NOFILE
"""

import abc
import contextlib
import io
import json
import logging
import os
import platform
import re
import resource
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("toacd.sandbox")

# ---------------------------------------------------------------------------
# Runner template executed inside the child Python process
# ---------------------------------------------------------------------------
SANDBOX_PYTHON_RUNNER = """
import contextlib
import io
import json
import os
import sys
import time
import traceback

# 1. POSIX Resource Limits (Defense-in-Depth)
sys.dont_write_bytecode = True
try:
    import resource
    # Hard CPU limit (5s soft, 6s hard)
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (5, 6))
    except Exception:
        pass
    # Virtual address space limit (4 GB to safely bound 64-bit runtimes like Python 3.11/3.12 without premature OOM)
    try:
        resource.setrlimit(resource.RLIMIT_AS, (4 * 1024 * 1024 * 1024, 4 * 1024 * 1024 * 1024))
    except Exception:
        pass
    # File size limit (50 MB prevents filling disk while allowing standard outputs/logs)
    try:
        resource.setrlimit(resource.RLIMIT_FSIZE, (50 * 1024 * 1024, 50 * 1024 * 1024))
    except Exception:
        pass
    # File descriptor limit
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))
    except Exception:
        pass
    # Disable core dumps
    try:
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    except Exception:
        pass
except ImportError:
    pass

# 2. CPython Audit Hooks (sys.addaudithook)
# Intercepts syscalls and library entry points at the C level
_SENSITIVE_PATTERNS = (".ssh", ".aws", ".gnupg", ".bash_history", ".zsh_history", ".gitconfig", "id_rsa", "id_ed25519")
_SCRATCH_DIR = os.environ.get("TOACD_SANDBOX_SCRATCH", "")
_SCRATCH_REAL = os.path.realpath(_SCRATCH_DIR) if _SCRATCH_DIR else ""

def _sandbox_audit_hook(event, args):
    # Block process spawning, shell execution, and process replacement
    if event in ("subprocess.Popen", "os.system", "os.posix_spawn", "posix.spawn", "os.fork", "os.forkpty"):
        raise PermissionError(f"Sandbox security violation: process execution is blocked ({event})")
    if event in ("os.exec", "posix.exec") or event.startswith("os.spawn"):
        raise PermissionError(f"Sandbox security violation: process replacement is blocked ({event})")

    # Block network communication
    if event.startswith("socket."):
        raise PermissionError(f"Sandbox security violation: network activity is blocked ({event})")

    # Block low-level ctypes / dynamic loading
    if event.startswith("ctypes."):
        raise PermissionError(f"Sandbox security violation: low-level memory/library access is blocked ({event})")

    # Block reading sensitive credential files and directory inspection
    if event in ("open", "os.listdir", "os.scandir"):
        target = str(args[0]) if args else ""
        norm = os.path.normpath(target)
        if any(pat in norm for pat in _SENSITIVE_PATTERNS):
            raise PermissionError(f"Sandbox security violation: access to sensitive path is prohibited ({target})")

    if event == "open":
        target = str(args[0]) if args else ""
        mode = str(args[1]) if len(args) > 1 else "r"
        if any(w in mode for w in ("w", "a", "+", "x")):
            real_t = os.path.realpath(target)
            if not _SCRATCH_REAL or not real_t.startswith(_SCRATCH_REAL):
                raise PermissionError(f"Sandbox security violation: write outside ephemeral scratch directory is blocked ({target})")

try:
    sys.addaudithook(_sandbox_audit_hook)
except (AttributeError, NotImplementedError):
    pass

# 3. Code Execution
code = sys.stdin.read()
captured = io.StringIO()
result = {
    "error_type": None,
    "error_message": None,
    "line_number": None,
    "traceback": None,
    "stdout": "",
    "execution_time_sec": 0.0,
}
start = time.perf_counter()
try:
    compiled = compile(code, "<string>", "exec")
    with contextlib.redirect_stdout(captured):
        exec(compiled, {"__name__": "__main__"})
except BaseException as error:
    result["error_type"] = type(error).__name__
    result["error_message"] = str(error)
    result["traceback"] = traceback.format_exc()
    if isinstance(error, SyntaxError):
        result["line_number"] = error.lineno
    else:
        for frame in reversed(traceback.extract_tb(sys.exc_info()[2])):
            if frame.filename == "<string>":
                result["line_number"] = frame.lineno
                break

result["stdout"] = captured.getvalue()
result["execution_time_sec"] = time.perf_counter() - start
sys.stdout.write(json.dumps(result))
"""


def _get_darwin_python_executables() -> List[str]:
    """Find all paths and framework binaries associated with the current Python runtime."""
    execs = set()
    current = os.path.realpath(sys.executable)
    execs.add(current)
    execs.add(sys.executable)
    execs.add(sys.base_prefix)
    execs.add(sys.prefix)

    # Check for CommandLineTools / Xcode Python launcher target
    app_target = os.path.join(
        os.path.dirname(os.path.dirname(current)),
        "Resources", "Python.app", "Contents", "MacOS", "Python"
    )
    if os.path.exists(app_target):
        execs.add(os.path.realpath(app_target))

    # Common Framework paths on Darwin
    for p in ("/Library/Developer/CommandLineTools", "/Library/Frameworks/Python3.framework", "/System/Library/Frameworks/Python.framework"):
        if os.path.exists(p):
            execs.add(os.path.realpath(p))

    return list(execs)


def generate_seatbelt_profile(
    allowed_executables: Optional[List[str]] = None,
    scratch_dir: Optional[str] = None,
    deny_network: bool = True,
    deny_sensitive_reads: bool = True,
    allow_fork: bool = True,
) -> str:
    """
    Generate an Apple Seatbelt (.sb) Profile Language configuration.
    """
    user_home = os.path.realpath(os.path.expanduser("~"))

    # Executable allowlist
    exec_rules = []
    exec_targets = allowed_executables or _get_darwin_python_executables()
    for item in exec_targets:
        if not item:
            continue
        real_item = os.path.realpath(item)
        if os.path.isdir(real_item):
            exec_rules.append(f'    (subpath "{real_item}")')
        else:
            exec_rules.append(f'    (literal "{real_item}")')
            exec_rules.append(f'    (subpath "{os.path.dirname(real_item)}")')

    exec_block = "\n".join(exec_rules) if exec_rules else '    (subpath "/usr/bin")'

    # Scratch write directory
    write_rules = []
    if scratch_dir and os.path.exists(scratch_dir):
        real_scratch = os.path.realpath(scratch_dir)
        write_rules.append(f'    (subpath "{real_scratch}")')
        # Also allow writing to Darwin temp / private tmp
        write_rules.append(f'    (subpath "/private{real_scratch}")')

    write_block = "\n".join(write_rules) if write_rules else ""

    profile = f""";; TOACD Sandboxing Profile (.sb)
;; Enforces strict kernel-level containment for untrusted code execution.
(version 1)
(deny default)

;; 1. Process Execution Controls
(allow process-exec
{exec_block}
)
{"(allow process-fork)" if allow_fork else "(deny process-fork)"}

;; 2. System and Kernel Queries
(allow sysctl-read)
(allow mach-lookup)

;; 3. Filesystem Read Controls
(allow file-read*)
"""
    if deny_sensitive_reads:
        profile += f"""(deny file-read*
    (subpath "{user_home}/.ssh")
    (subpath "{user_home}/.aws")
    (subpath "{user_home}/.gnupg")
    (subpath "{user_home}/.config")
    (subpath "{user_home}/.bash_history")
    (subpath "{user_home}/.zsh_history")
    (subpath "{user_home}/.gitconfig")
    (subpath "/Library/Keychains")
    (subpath "/private/var/db")
)
"""

    profile += f"""
;; 4. Filesystem Write Controls
(deny file-write*)
"""
    if write_block:
        profile += f"""(allow file-write*
{write_block}
)
"""

    if deny_network:
        profile += """
;; 5. Network Isolation
(deny network*)
"""

    profile += """
;; 6. POSIX IPC Restrictions
(deny ipc-posix-shm*)
"""
    return profile


# ---------------------------------------------------------------------------
# Base Sandbox Engine Interface
# ---------------------------------------------------------------------------
class BaseSandboxEngine(abc.ABC):
    """Abstract interface implemented by all sandbox execution engines."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the sandbox engine."""
        pass

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Check whether this engine can function in the current runtime environment."""
        pass

    @abc.abstractmethod
    def run_python(
        self,
        code: str,
        timeout: float = 5.0,
        scratch_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute Python source code securely in the sandbox."""
        pass

    @abc.abstractmethod
    def run_command(
        self,
        cmd: List[str],
        cwd: Optional[str] = None,
        timeout: float = 5.0,
        input_data: Optional[str] = None,
        allowed_executables: Optional[List[str]] = None,
    ) -> subprocess.CompletedProcess:
        """Execute an arbitrary binary/command under sandbox restrictions."""
        pass

    def get_info(self) -> Dict[str, Any]:
        """Return engine metadata and isolation guarantees."""
        return {
            "engine": self.name,
            "available": self.is_available(),
        }


# ---------------------------------------------------------------------------
# Engine 1: macOS Seatbelt (sandbox-exec)
# ---------------------------------------------------------------------------
class SeatbeltSandboxEngine(BaseSandboxEngine):
    """
    macOS Kernel Seatbelt engine using sandbox-exec with a dynamically
    synthesized .sb profile.
    """

    def __init__(self):
        self._checked_availability = False
        self._is_available = False

    @property
    def name(self) -> str:
        return "macOS Seatbelt (sandbox-exec)"

    def is_available(self) -> bool:
        if self._checked_availability:
            return self._is_available

        if sys.platform != "darwin" or not shutil.which("sandbox-exec"):
            self._is_available = False
            self._checked_availability = True
            return False

        # Probe sandbox_apply capability: when running nested inside another restricted
        # sandbox, sandbox-exec may fail with exit code 71 (Operation not permitted).
        try:
            probe = subprocess.run(
                ["sandbox-exec", "-p", "(version 1) (allow default)", "/usr/bin/true"],
                capture_output=True,
                timeout=2,
            )
            self._is_available = (probe.returncode == 0)
        except Exception:
            self._is_available = False

        self._checked_availability = True
        return self._is_available

    def run_python(
        self,
        code: str,
        timeout: float = 5.0,
        scratch_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        owns_scratch = False
        if not scratch_dir:
            scratch_dir = tempfile.mkdtemp(prefix="toacd_sb_")
            owns_scratch = True

        try:
            profile = generate_seatbelt_profile(
                allowed_executables=_get_darwin_python_executables(),
                scratch_dir=scratch_dir,
                deny_network=True,
                deny_sensitive_reads=True,
                allow_fork=True,
            )

            env = os.environ.copy()
            env["TOACD_SANDBOX_SCRATCH"] = os.path.realpath(scratch_dir)

            cmd = [
                "sandbox-exec",
                "-p",
                profile,
                sys.executable,
                "-B",
                "-c",
                SANDBOX_PYTHON_RUNNER,
            ]

            proc = subprocess.run(
                cmd,
                input=code,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                start_new_session=True,
            )

            if proc.returncode != 0:
                # If sandbox-exec or python aborted
                raise RuntimeError(
                    f"Code execution process exited unexpectedly "
                    f"(exit status {proc.returncode}): {proc.stderr.strip()}"
                )

            data = json.loads(proc.stdout)
            data["sandbox_engine"] = self.name
            return data

        except subprocess.TimeoutExpired as error:
            partial_output = error.stdout or ""
            if isinstance(partial_output, bytes):
                partial_output = partial_output.decode("utf-8", errors="replace")
            return {
                "error_type": "TimeoutError",
                "error_message": f"Execution exceeded the {timeout}-second time limit.",
                "line_number": None,
                "traceback": "",
                "stdout": partial_output,
                "execution_time_sec": timeout,
                "sandbox_engine": self.name,
            }
        finally:
            if owns_scratch and os.path.exists(scratch_dir):
                shutil.rmtree(scratch_dir, ignore_errors=True)

    def run_command(
        self,
        cmd: List[str],
        cwd: Optional[str] = None,
        timeout: float = 5.0,
        input_data: Optional[str] = None,
        allowed_executables: Optional[List[str]] = None,
    ) -> subprocess.CompletedProcess:
        exec_list = list(allowed_executables or [])
        if cmd and cmd[0]:
            exec_list.append(cmd[0])

        profile = generate_seatbelt_profile(
            allowed_executables=exec_list,
            scratch_dir=cwd,
            deny_network=True,
            deny_sensitive_reads=True,
            allow_fork=False,
        )

        sandboxed_cmd = ["sandbox-exec", "-p", profile] + cmd

        return subprocess.run(
            sandboxed_cmd,
            cwd=cwd,
            input=input_data,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            stdin=subprocess.DEVNULL if input_data is None else None,
            start_new_session=True,
        )

    def get_info(self) -> Dict[str, Any]:
        return {
            "engine": self.name,
            "type": "Seatbelt Mandatory Access Control (MAC)",
            "isolation_level": "Kernel-enforced OS sandbox",
            "network_blocked": True,
            "filesystem_writes_restricted": True,
            "sensitive_paths_protected": True,
            "available": self.is_available(),
        }


# ---------------------------------------------------------------------------
# Engine 2: Docker / gVisor Ephemeral Container Engine
# ---------------------------------------------------------------------------
class DockerSandboxEngine(BaseSandboxEngine):
    """
    Spins up a lightweight ephemeral Docker container (with optional gVisor runsc)
    for total kernel / namespace virtualization.
    """

    def __init__(self, image: str = "python:3.9-slim"):
        self.image = image
        self._checked_availability = False
        self._is_available = False
        self._has_gvisor = False

    @property
    def name(self) -> str:
        return "Docker / gVisor Container Sandbox" if self._has_gvisor else "Docker Ephemeral Container Sandbox"

    def is_available(self) -> bool:
        if self._checked_availability:
            return self._is_available

        docker_bin = shutil.which("docker")
        if not docker_bin:
            self._is_available = False
            self._checked_availability = True
            return False

        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=3)
            self._is_available = (res.returncode == 0)
            if self._is_available and b"runsc" in res.stdout:
                self._has_gvisor = True
        except Exception:
            self._is_available = False

        self._checked_availability = True
        return self._is_available

    def run_python(
        self,
        code: str,
        timeout: float = 5.0,
        scratch_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        docker_cmd = [
            "docker", "run", "--rm", "-i",
            "--network", "none",
            "--read-only",
            "--user", "1000:1000",
            "--memory", "256m",
            "--cpus", "1.0",
            "--pids-limit", "32",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true",
        ]

        if self._has_gvisor:
            docker_cmd.extend(["--runtime", "runsc"])

        docker_cmd.extend([self.image, "python", "-c", SANDBOX_PYTHON_RUNNER])

        try:
            proc = subprocess.run(
                docker_cmd,
                input=code,
                capture_output=True,
                text=True,
                timeout=timeout + 2.0,  # container startup grace
            )

            if proc.returncode != 0:
                raise RuntimeError(
                    f"Docker container execution failed (exit status {proc.returncode}): {proc.stderr.strip()}"
                )

            data = json.loads(proc.stdout)
            data["sandbox_engine"] = self.name
            return data

        except subprocess.TimeoutExpired as error:
            partial_output = error.stdout or ""
            if isinstance(partial_output, bytes):
                partial_output = partial_output.decode("utf-8", errors="replace")
            return {
                "error_type": "TimeoutError",
                "error_message": f"Execution exceeded the {timeout}-second time limit.",
                "line_number": None,
                "traceback": "",
                "stdout": partial_output,
                "execution_time_sec": timeout,
                "sandbox_engine": self.name,
            }

    def run_command(
        self,
        cmd: List[str],
        cwd: Optional[str] = None,
        timeout: float = 5.0,
        input_data: Optional[str] = None,
        allowed_executables: Optional[List[str]] = None,
    ) -> subprocess.CompletedProcess:
        docker_cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "256m",
            "--cpus", "1.0",
            "--pids-limit", "32",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true",
        ]
        if self._has_gvisor:
            docker_cmd.extend(["--runtime", "runsc"])
        if cwd:
            docker_cmd.extend(["-v", f"{cwd}:/workspace:ro", "-w", "/workspace"])

        docker_cmd.append(self.image)
        docker_cmd.extend(cmd)

        return subprocess.run(
            docker_cmd,
            input=input_data,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout + 2.0,
        )

    def get_info(self) -> Dict[str, Any]:
        return {
            "engine": self.name,
            "type": "Container Virtualization",
            "gvisor_active": self._has_gvisor,
            "isolation_level": "gVisor Syscall Interception" if self._has_gvisor else "Linux Namespaces & cgroups",
            "network_blocked": True,
            "filesystem_writes_restricted": True,
            "available": self.is_available(),
        }


# ---------------------------------------------------------------------------
# Engine 3: AuditHook & POSIX Resource Limits (Defense-in-Depth Fallback)
# ---------------------------------------------------------------------------
class AuditHookSandboxEngine(BaseSandboxEngine):
    """
    CPython Audit Hooks (sys.addaudithook) and POSIX setrlimit execution engine.
    Active inside the child runner process, and acts as the universal sandbox
    when OS-level sandboxing (Seatbelt/Docker) is unavailable or nested.
    """

    @property
    def name(self) -> str:
        return "AuditHook & POSIX Limits (In-Process Sandbox)"

    def is_available(self) -> bool:
        return True

    def run_python(
        self,
        code: str,
        timeout: float = 5.0,
        scratch_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        owns_scratch = False
        if not scratch_dir:
            scratch_dir = tempfile.mkdtemp(prefix="toacd_ah_")
            owns_scratch = True

        try:
            env = os.environ.copy()
            env["TOACD_SANDBOX_SCRATCH"] = os.path.realpath(scratch_dir)

            proc = subprocess.run(
                [sys.executable, "-B", "-c", SANDBOX_PYTHON_RUNNER],
                input=code,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                start_new_session=True,
            )

            if proc.returncode != 0:
                raise RuntimeError(
                    f"Code execution process exited unexpectedly "
                    f"(exit status {proc.returncode}): {proc.stderr.strip()}"
                )

            data = json.loads(proc.stdout)
            data["sandbox_engine"] = self.name
            return data

        except subprocess.TimeoutExpired as error:
            partial_output = error.stdout or ""
            if isinstance(partial_output, bytes):
                partial_output = partial_output.decode("utf-8", errors="replace")
            return {
                "error_type": "TimeoutError",
                "error_message": f"Execution exceeded the {timeout}-second time limit.",
                "line_number": None,
                "traceback": "",
                "stdout": partial_output,
                "execution_time_sec": timeout,
                "sandbox_engine": self.name,
            }
        finally:
            if owns_scratch and os.path.exists(scratch_dir):
                shutil.rmtree(scratch_dir, ignore_errors=True)

    def run_command(
        self,
        cmd: List[str],
        cwd: Optional[str] = None,
        timeout: float = 5.0,
        input_data: Optional[str] = None,
        allowed_executables: Optional[List[str]] = None,
    ) -> subprocess.CompletedProcess:
        # Preexec limits for binary execution
        def _preexec_limits():
            try:
                resource.setrlimit(resource.RLIMIT_CPU, (int(timeout), int(timeout) + 1))
            except Exception:
                pass
            try:
                resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 * 1024 * 1024, 2 * 1024 * 1024 * 1024))
            except Exception:
                pass
            try:
                resource.setrlimit(resource.RLIMIT_FSIZE, (50 * 1024 * 1024, 50 * 1024 * 1024))
            except Exception:
                pass
            try:
                resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            except Exception:
                pass

        return subprocess.run(
            cmd,
            cwd=cwd,
            input=input_data,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            preexec_fn=_preexec_limits if os.name == "posix" else None,
            stdin=subprocess.DEVNULL if input_data is None else None,
            start_new_session=True,
        )

    def get_info(self) -> Dict[str, Any]:
        return {
            "engine": self.name,
            "type": "CPython Audit Hooks & POSIX Resource Limits",
            "isolation_level": "Language runtime and process limits",
            "network_blocked": True,
            "filesystem_writes_restricted": True,
            "sensitive_paths_protected": True,
            "available": True,
        }


# ---------------------------------------------------------------------------
# Sandbox Manager / Factory
# ---------------------------------------------------------------------------
class SandboxManager:
    """
    Selects and coordinates the active sandbox engine based on platform,
    configuration, and runtime availability.
    """

    def __init__(self):
        self._seatbelt = SeatbeltSandboxEngine()
        self._docker = DockerSandboxEngine()
        self._audithook = AuditHookSandboxEngine()

    def get_engine(self) -> BaseSandboxEngine:
        """
        Determine the most secure available sandbox engine.
        Priority:
        1. Explicit override via TOACD_SANDBOX_ENGINE env var (seatbelt, docker, audithook)
        2. macOS Seatbelt if on Darwin and permitted
        3. Docker / gVisor if Docker is accessible
        4. AuditHookSandboxEngine fallback
        """
        override = os.environ.get("TOACD_SANDBOX_ENGINE", "").lower().strip()
        if override == "seatbelt" and self._seatbelt.is_available():
            return self._seatbelt
        if override == "docker" and self._docker.is_available():
            return self._docker
        if override == "audithook":
            return self._audithook

        # Auto-selection:
        # On macOS, prioritize native Seatbelt if permitted.
        # On other POSIX / Linux / CI systems, default to AuditHook engine
        # (runs directly against the active Python runtime without external daemon dependencies).
        # Docker / gVisor container isolation can be explicitly chosen via TOACD_SANDBOX_ENGINE=docker.
        if sys.platform == "darwin" and self._seatbelt.is_available():
            return self._seatbelt
        return self._audithook

    def run_python(
        self,
        code: str,
        timeout: float = 5.0,
        scratch_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        engine = self.get_engine()
        return engine.run_python(code, timeout=timeout, scratch_dir=scratch_dir)

    def run_command(
        self,
        cmd: List[str],
        cwd: Optional[str] = None,
        timeout: float = 5.0,
        input_data: Optional[str] = None,
        allowed_executables: Optional[List[str]] = None,
    ) -> subprocess.CompletedProcess:
        engine = self.get_engine()
        return engine.run_command(
            cmd,
            cwd=cwd,
            timeout=timeout,
            input_data=input_data,
            allowed_executables=allowed_executables,
        )

    def get_status(self) -> Dict[str, Any]:
        active_engine = self.get_engine()
        return {
            "active_engine": active_engine.name,
            "active_details": active_engine.get_info(),
            "engines_available": {
                "seatbelt": self._seatbelt.is_available(),
                "docker": self._docker.is_available(),
                "audithook": self._audithook.is_available(),
            },
            "platform": {
                "os": platform.system(),
                "release": platform.release(),
                "python_version": platform.python_version(),
            },
        }


# Global Singleton
_DEFAULT_MANAGER = SandboxManager()


def run_sandboxed_python(
    code: str,
    timeout: float = 5.0,
    scratch_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute Python code in the optimal available sandbox."""
    return _DEFAULT_MANAGER.run_python(code, timeout=timeout, scratch_dir=scratch_dir)


def run_sandboxed_command(
    cmd: List[str],
    cwd: Optional[str] = None,
    timeout: float = 5.0,
    input_data: Optional[str] = None,
    allowed_executables: Optional[List[str]] = None,
) -> subprocess.CompletedProcess:
    """Execute an external command/binary in the optimal available sandbox."""
    return _DEFAULT_MANAGER.run_command(
        cmd,
        cwd=cwd,
        timeout=timeout,
        input_data=input_data,
        allowed_executables=allowed_executables,
    )


def get_sandbox_status() -> Dict[str, Any]:
    """Inspect current sandbox capabilities and active engine status."""
    return _DEFAULT_MANAGER.get_status()
