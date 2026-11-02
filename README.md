# IntelliFix

IntelliFix is a local Flask web app for diagnosing and repairing Python code.
It combines a small set of static checks, subprocess-based execution, readable
error explanations, and rule-based automatic fixes. It does not use an AI
model: explanations and fixes are deterministic rules.

## What it does

When you analyze a sample or uploaded Python file, the app:

1. Scans the source for selected risky patterns. Critical and high severity
   findings block analysis and execution.
2. Checks syntax and a limited set of static issues, including undefined names,
   obvious string/number addition mismatches, and division by a literal zero.
3. If static analysis finds no issue, runs the code in a child Python process
   with a five-second timeout and captures its output or exception.
4. Shows an error explanation and, when a rule is available, proposes a fix.
   The bounded repair loop makes at most five attempts. A candidate fix is
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

The analysis view reports the measured subprocess execution time. Emissions and
energy are zero unless CodeCarbon is installed and tracking is enabled:

```bash
USE_CODECARBON=1 python gui.py
```

CodeCarbon measurements depend on the host environment and may not be available
for every run. The `/analytics` dashboard uses generated illustrative data; its
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
| `POST /api/save` | Save code as a separate fixed file |
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

There is no `main.py` command-line application or `evaluation.py` module in the
current project. Start the app with `python gui.py` or `python app.py`.

## Security and limitations

The execution subprocess has a five-second timeout, but it is **not an
operating-system sandbox**: executed code has the same OS permissions as the
server process. The AST security scanner checks a limited blocklist and can be
bypassed. Do not expose this app to untrusted users or run untrusted code on a
machine with sensitive data.

The app also limits submitted code to 100 KB on its relevant endpoints.
Python's parser reports syntax errors one at a time; the static checks can
collect multiple semantic findings only when the source parses successfully.
Automatic fixes are limited to the rules implemented in `nlp_explainer.py`;
some errors receive an explanation without a fix.
