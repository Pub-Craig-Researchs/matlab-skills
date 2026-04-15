---
name: matlab-doc-injector
description: >
  Query local MATLAB function documentation and inject high-density Markdown into Agent context.
  Use when writing MATLAB code and needing official function references (syntax, parameters, examples).
  Triggers: MATLAB function queries, parameter clarification, avoiding hallucination for toolbox functions.
  PREREQUISITE: MATLAB documentation must be downloaded locally and MDI tool must be installed and initialized.
---

# MATLAB Doc Injector (MDI)

Query MATLAB's offline HTML documentation and convert it to LLM-friendly Markdown.

## Prerequisites

**MANDATORY**: MATLAB documentation must already be downloaded locally.

MDI does NOT download documentation. It only indexes and parses existing local MATLAB installations.

### Installation (First Time Only)

The skill is self-contained. Install from the skill directory:

```bash
# Navigate to the skill directory
cd .qoder/skills/matlab-doc-injector

# Create virtual environment and install
uv venv --python 3.12
uv pip install -e .

# Or with standard pip
python -m pip install -e .
```

### First-Time Setup

Initialize MDI after installation:

```bash
# Auto-detect MATLAB and build index
mdi --init --workers 0

# Verify setup
mdi --stats
```

If MATLAB is not auto-detected, specify the path:

```bash
# Windows example
mdi --matlab-path "C:\Program Files\MATLAB\R2025b" --init --workers 0
# or your version: mdi --matlab-path "C:\Program Files\MATLAB\R2024a" --init --workers 0

# Linux example  
mdi --matlab-path /usr/local/MATLAB/R2025b --init --workers 0

# macOS example
mdi --matlab-path /Applications/MATLAB_R2025b.app --init --workers 0
```

### Verification

Run environment check:
```bash
mdi --stats
```

Expected output shows indexed functions (>0). If `Total Functions: 0`, run `mdi --init`.

## Quick Start

```bash
# Terminal output
mdi fmincon

# Save to file
mdi fmincon -o ./docs/

# Raw output (no denoising)
mdi fmincon --raw
```

## Workflow

### Step 1: Check Status
```bash
mdi --stats
```

### Step 2: Query Documentation
```bash
# Single function (cache hit: <10ms)
mdi plot

# With file output
mdi optimoptions -o ./matlab-docs/
```

### Step 3: Use in Context

Markdown output contains:
- Function syntax and signatures
- Input/output argument tables
- Code examples
- Mathematical formulations
- Option parameters

## CLI Reference

```
mdi [function] [options]

Query:
  function              MATLAB function name
  -o, --output PATH     Output directory
  --raw                 Raw Markdown (no denoising)

Index Management:
  --init                Rebuild index
  --update              Incremental update
  --stats               Show statistics

Configuration:
  --matlab-path PATH    Specify MATLAB root
  --workers N           Threads: 1=default, 0=auto
  -v, --verbose         Debug logging
```

## Common Use Cases

### Optimization
```bash
mdi fmincon          # Constrained optimization
mdi linprog          # Linear programming
mdi ga               # Genetic algorithm
mdi optimoptions     # Options reference
```

### Signal Processing
```bash
mdi fft              # FFT
mdi filter           # Filtering
mdi spectrogram      # Time-frequency
```

### Statistics & ML
```bash
mdi fitlm            # Linear model
mdi pca              # PCA
mdi trainNetwork     # Deep learning
```

## Troubleshooting

### Function Not Found
```bash
mdi --update  # Refresh index
```

### Slow First Query
First query parses HTML (~500ms), subsequent use cache (<10ms).

### Multiple MATLAB Versions
```bash
mdi --matlab-path "<your-matlab-path>" fmincon
```

## Performance

- **Index build**: ~3s for 95k functions (24 threads)
- **Cache hit**: <10ms
- **Cache miss**: <500ms
- **Database**: ~30MB

## Denoising

Removes: Navigation links, copyright info, buttons
Preserves: Syntax, parameters, examples, equations

Use `--raw` for full output.
