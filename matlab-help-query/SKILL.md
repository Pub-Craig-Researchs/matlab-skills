---
name: matlab-help-query
description: >
  Query MATLAB function documentation using MATLAB CLI's help command.
  Use when the agent needs to look up MATLAB function syntax, parameters, examples, or usage information.
  Triggers: MATLAB function queries, parameter clarification, syntax lookup, exploring unfamiliar functions.
  Works for built-in functions, toolbox functions, and user-defined functions on the MATLAB path.
---

# MATLAB Help Query

Query MATLAB function documentation using the CLI `help` command.

## When to Use

- Need to check function syntax or signatures
- Looking for parameter descriptions
- Need usage examples
- Exploring unfamiliar MATLAB functions
- Verifying function availability

## Quick Start

### Basic Query

```bash
matlab -batch "help functionName"
```

Examples:
```bash
matlab -batch "help plot"
matlab -batch "help fmincon"
matlab -batch "help readtable"
```

### Query with Output Capture

For clean, programmatic access to help text:

```bash
matlab -batch "disp(evalc('help plot'))"
```

## Workflow

### Step 1: Check if Function Exists

```bash
matlab -batch "if exist('functionName', 'file'), disp('Found'); else, disp('Not found'); end"
```

Check return value:
```bash
matlab -batch "retval = exist('functionName', 'file'); disp(retval)"
# Returns:
# 2 - M-file
# 3 - MEX-file
# 5 - P-file
# 6 - MDL-file (Simulink)
# 8 - class
# 0 - not found
```

### Step 2: Get Help Information

```bash
# Quick help (displays to terminal)
matlab -batch "help functionName"

# Capture help text (recommended for processing)
matlab -batch "disp(evalc('help functionName'))"

# For detailed documentation (opens browser, interactive only)
matlab -batch "web(fullfile(docroot, 'matlab/ref/functionName.html'))"
```

### Step 3: Handle Special Cases

**Built-in functions:**
```bash
matlab -batch "help builtin_functionName"
```

**Method of a class:**
```bash
matlab -batch "help className.methodName"
```

**Package function:**
```bash
matlab -batch "help +packageName.functionName"
```

## CLI Usage

When running from terminal (non-interactive):

```bash
# MATLAB R2019a+ (recommended)
matlab -batch "help('plot')"

# Older versions (R2018a and earlier)
matlab -r "help('plot'); exit"
```

**Key differences:**
- `-batch`: No GUI, no interactive prompts, auto-exits (R2019a+)
- `-r`: Opens MATLAB window, requires manual `exit`, may have prompts

### Windows PowerShell Example

```powershell
# Capture output to variable
$output = matlab -batch "evalc('help fmincon')" 2>&1
$output -join "`n"

# Or redirect to file
matlab -batch "help fmincon" > help_output.txt 2>&1
```

### Linux/macOS Example

```bash
# Capture output
matlab -batch "evalc('help plot')" > help_output.txt 2>&1

# Direct display
matlab -batch "help fmincon"
```

### Best Practice: Use evalc for Clean Output

```bash
# Without evalc: includes extra newlines and formatting
matlab -batch "help('fmincon')"

# With evalc: clean, capture-ready output
matlab -batch "disp(evalc('help fmincon'))"
```

## Common Patterns

### Get Function Syntax Only

```bash
# Get first 10 lines (usually contains syntax)
matlab -batch "h = evalc('help functionName'); lines = strsplit(h, '\n'); disp(strjoin(lines(1:min(10, numel(lines))), '\n'))"
```

### Search for Functions by Topic

```bash
matlab -batch "lookfor keyword"
# Example:
matlab -batch "lookfor optimization"
```

### Get Help on Multiple Functions

```bash
matlab -batch "funcs = {'plot', 'scatter', 'bar'}; for i = 1:numel(funcs), fprintf('=== %s ===\n', funcs{i}); evalc('help', funcs{i}); fprintf('\n'); end"
```

Or use a script file for complex queries:
```bash
# Create help_batch.m
# funcs = {'plot', 'scatter', 'bar'};
# for i = 1:numel(funcs)
#     fprintf('=== %s ===\n', funcs{i});
#     help(funcs{i});
#     fprintf('\n');
# end

matlab -batch "help_batch"
```

## Error Handling

| Scenario | Solution |
|----------|----------|
| Function not found | Check spelling, verify toolbox availability |
| Empty help | Function may be private or not on path |
| "Help not available" | Try `doc functionName` or check MathWorks website |

### Fallback Strategy

```bash
# Try help first, fallback to lookfor if not found
matlab -batch "try, disp(evalc('help unknownFunc')); catch, fprintf('Direct help failed, trying lookfor...\n'); disp(evalc('lookfor unknownFunc')); end"
```

Or use a script for better readability:

```bash
# Create query_help.m with the following content:
# funcName = 'unknownFunc';
# try
#     helpText = evalc(['help ', funcName]);
#     if isempty(strtrim(helpText))
#         error('Empty help');
#     end
#     disp(helpText);
# catch
#     fprintf('Direct help failed, trying lookfor...\n');
#     lookforResult = evalc(['lookfor ', funcName]);
#     disp(lookforResult);
# end

matlab -batch "query_help"
```

## Performance Tips

- `matlab -batch` startup time: ~2-5 seconds (one-time cost)
- `help` command itself is fast (<100ms)
- Use `evalc()` to capture clean output without extra formatting
- For batch queries, create a script file instead of multiple CLI calls
- Cache results to files if querying the same functions repeatedly

## Notes

- `help` shows the comment block at the top of M-files
- For toolbox functions, ensure the toolbox is installed
- `doc` provides more comprehensive info but requires browser (interactive only)
- In non-interactive environments (scripts, automation), use `-batch` with `help`
- Use `-batch` (R2019a+) over `-r` for cleaner automation
