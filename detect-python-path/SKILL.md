---
name: detect-python-path
description: >
  Detect the Python interpreter's absolute path via MATLAB pyenv.
  Trigger this skill whenever the agent needs to call Python from the terminal
  (run_in_terminal) — e.g., running scripts, pip install, debugging modules.
  Avoids the pitfall where `python`/`where python`/`which python` cannot find
  conda or virtualenv interpreters.
---

# Detect Python Path

Retrieve the Python executable's absolute path from MATLAB `pyenv` for reliable terminal invocation.

## Why

- The `python` alias may point to the wrong version or not exist at all.
- `where python` (Windows) / `which python` (Linux/macOS) **cannot** find conda/venv interpreters.
- MATLAB `pyenv` already stores the project's actual Python path — the most reliable source.

## Workflow

### 1. Get the path

Run via MATLAB MCP:

```matlab
pe = pyenv;
disp(pe.Executable)
```

The returned value is the absolute path (e.g. `C:\Users\...\python.exe`).

### 2. Handle unconfigured pyenv

If `pe.Executable` is an empty string (`""`), MATLAB has no Python configured:
- **Ask the user** for their Python environment path.
- Use the confirmed absolute path going forward.

### 3. Use the path

All terminal Python calls must use the absolute path:

```
<absolute_path> script.py
<absolute_path> -m pip install <package>
```

**Never** use bare `python` or `python3`.

## Notes

- Paths differ across machines and environments — **never assume a fixed path**.
- Retrieve once per project/session; reuse afterwards.
- In PowerShell, `python -c "..."` has quoting conflicts — write a script file instead.
