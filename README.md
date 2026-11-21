# IntelliFix

IntelliFix is a local Flask web app for diagnosing and repairing Python code.
It combines a small set of static checks, subprocess-based execution, readable
error explanations, and rule-based automatic fixes. It does not use an AI model:
explanations and fixes are deterministic rules.

## What it does

When you analyze a sample or uploaded Python file, the app:

1. Scans the source for selected risky patterns. Critical and high severity
   findings block analysis and execution.
2. Checks syntax and a limited set of static issues, including undefined names,
   obvious string/number addition mismatches, and division by a literal zero.
3. If static analysis finds no issue, runs the code in a child Python process
   with a five-second timeout and captures its output or exception.
4. Shows an error explanation and, when a rule is available, proposes a fix.
   The bounded repair loop makes at most 100 attempts (with a 60-second time
   budget). A candidate fix is
   checked for newly introduced vulnerability types and can be verified by
   analyzing and running it again.

Static analysis reports only the checks implemented by this project; it is
not a complete Python type checker or security analyzer.

## Requirements and startup

Use Python with `pip`, then install the packages from the project root:

```bash
python -m pip install -r requirements.txt
python gui.py
```

Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser. The app
binds to localhost on port 5001. You can also start the Flask app directly:

```bash
python app.py
```

To stop the server, press `Ctrl+C` in the terminal.

## Using the web app

- The studio opens with a blank, unsaved file. Type code, then scan or run it; use
  **Save** to name and save it as a new file without replacing a sample.
- Choose **New** at any time to start another blank file.
- Select a listed sample file, or upload a `.py` file.
- Choose **Scan & Diagnose Error** to analyze it and view the diagnostic,
  suggested code, and measured execution metrics.
- Edit the suggested code as needed. **Save Modification** writes a separate
  `*_fixed.py` file rather than overwriting the original.
- **Run Modified Code** executes the edited code and displays its output.
- Open **View Eco Analytics** for the illustrative analytics dashboard.

Uploads are stored in the project working directory with a `test_upload_`
prefix. Uploaded code is not executed until you explicitly analyze or run it.

## Metrics

The analysis view reports the measured subprocess execution time. To measure
CodeCarbon emissions for the lifetime of the web server, install CodeCarbon
in the active Python environment and start the GUI with:

```bash
USE_CODECARBON=1 python gui.py
```

The server prints its total measured emissions in mg CO2-eq when it exits
(including when stopped with `Ctrl+C`). During this mode, CodeCarbon does not
start a second overlapping tracker for each analysis. CodeCarbon measurements
depend on the host environment and may be zero or unavailable for short runs.
The `/analytics` dashboard reads CodeCarbon's output file; its other illustrative
charts are not benchmark results or measurements of the current analysis.

## API routes

The Flask app also exposes these routes:

| Route | Purpose |
|---|---|
| `GET /` | Main web studio |
| `GET /analytics` | Illustrative analytics dashboard |
| `GET /api/files` | List available sample and fixed files |
| `GET /api/source?filename=...` | Read an allowed file |
| `POST /api/file` | Read an allowed file (used by the web UI) |
| `POST /api/analyze` | Security scan, diagnose, explain, and suggest a fix |
| `POST /api/execute` | Security scan and execute submitted code |
| `POST /api/save` | Save code as a separate fixed file, or create a named new file |
| `POST /api/upload` | Save an uploaded Python file without running it |
| `GET /api/analytics` | Return illustrative analytics data |

The JSON request and response shapes are implemented in `app.py` and used by
the bundled web UI.

## Project files

- `app.py` — Flask application, routes, repair loop, and fix verification
- `gui.py` — local web server launcher
- `static_analyzer.py` — AST-based static checks
- `security_analyzer.py` — AST-based checks for selected risky patterns
- `error_extractor.py` — analysis and child-process execution
- `ir_generator.py` — structured diagnostic data
- `nlp_explainer.py` — rule-based explanations and fixes
- `templates/` — web studio and analytics pages
- `test*.py` — sample Python files shown in the studio
- `run_checks.py` — batch diagnostic/repair checks for selected samples
- `check_word2number.py` — checks number-word `ValueError` fixes such as `int('seventeen')`
- `sandbox.py` — multi-engine secure sandbox implementation (macOS Seatbelt, Docker/gVisor, CPython audit hooks)
- `sandbox_profile.sb` — Apple Seatbelt profile language (.sb) configuration for kernel containment
- `test_sandbox.py` — comprehensive security test suite validating sandbox isolation and attack containment

There is no `main.py` command-line application or `evaluation.py` module in the
current project. Start the app with `python gui.py` or `python app.py`.

## Sandboxing and Security Architecture

TOACD utilizes a multi-layered, defense-in-depth **Sandbox Engine** (`sandbox.py`) to execute untrusted code without exposing the host system:

1. **macOS Native Seatbelt (`sandbox-exec` with `.sb` profile)**:
   - **Kernel-Enforced Mandatory Access Control (MAC)** via Apple Seatbelt Profile Language (`sandbox_profile.sb`).
   - **Zero Network Access**: Completely disables outbound and inbound socket creation (`(deny network*)`).
   - **Read-Only Host Filesystem**: Arbitrary file creation/modification is denied globally (`(deny file-write*)`). Writes are confined exclusively to isolated ephemeral scratch directories.
   - **Credential Protection**: Explicitly prohibits reading sensitive user configurations, keys, and dotfiles (`~/.ssh`, `~/.aws`, `~/.gnupg`, `~/.bash_history`, `~/.zsh_history`, `/Library/Keychains`).
   - **Restricted Process Execution**: Prohibits executing arbitrary binaries (`/bin/sh`, `/bin/bash`, `rm`, `curl`) by whitelisting only designated runtime binaries.

2. **Ephemeral Docker / gVisor Container Engine**:
   - For containerized or Linux deployments, untrusted code is executed inside ephemeral containers (`--rm -i --network none --read-only --user 1000:1000 --cap-drop ALL --memory 256m --cpus 1.0`).
   - Supports optional gVisor (`--runtime runsc`) for hardware-independent syscall interception.

3. **In-Process Defense-in-Depth (Audit Hooks & POSIX Resource Limits)**:
   - CPython 3.8+ audit hooks (`sys.addaudithook`) intercept subprocess calls (`subprocess.Popen`, `os.system`), network activity (`socket.*`), ctypes tampering, and sensitive path access at the interpreter level.
   - POSIX `resource.setrlimit` enforces hard CPU time limits (`RLIMIT_CPU`), virtual memory bounds (`RLIMIT_AS`), file size write limits (`RLIMIT_FSIZE`), and descriptor limits (`RLIMIT_NOFILE`).

Sandbox engine status and capabilities can be inspected at runtime via `get_sandbox_status()` or the `/api/sandbox/status` REST endpoint. Run the security verification suite with:
```bash
python test_sandbox.py
```

The app also limits submitted code to 100 KB on its relevant endpoints.
Python's parser reports syntax errors one at a time; the static checks can
collect multiple semantic findings only when the source parses successfully.
Automatic fixes are limited to the rules implemented in `nlp_explainer.py`;
some errors receive an explanation without a fix.
