# MATLAB Doc Injector - Skill for AI Agents

This skill enables AI agents to query local MATLAB documentation and inject it into their context.

## For Users

### Quick Setup (First Time)

The skill is self-contained. Install directly from the skill directory:

```bash
# Navigate to the skill directory
cd .qoder/skills/matlab-doc-injector

# Create virtual environment
uv venv --python 3.12

# Install MDI and all dependencies
uv pip install -e .

# Or with standard pip
python -m pip install -e .
```

### Initialize

```bash
# Auto-detect MATLAB and build index
mdi --init --workers 0

# Verify setup
mdi --stats
```

### Use

```bash
mdi fmincon
mdi plot -o ./docs/
```

### Requirements

- Python 3.12+
- MATLAB installed locally
- uv (recommended) or pip

## For AI Agents

When this skill triggers:
1. Read `SKILL.md` for usage instructions
2. Check if `mdi` is available (`mdi --version`)
3. If not installed, guide user through setup from the skill directory
4. Use `mdi <function>` to query documentation
5. Inject Markdown output into your context

## Structure

```
matlab-doc-injector/
├── SKILL.md           # Skill instructions for agents
├── README.md          # Human-readable setup guide
├── pyproject.toml     # Python project configuration
├── mdi/               # MDI source code (self-contained)
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── config.py
│   ├── cache.py
│   ├── indexer.py
│   └── parser.py
└── agents/
    └── agent.yaml     # UI metadata
```

The skill is completely self-contained. All MDI source code is included, and each user's MATLAB path is auto-detected or manually specified during first-time setup.
