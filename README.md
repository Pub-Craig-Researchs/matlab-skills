# MATLAB Skills

This is a repository that archives personal MATLAB skills, utilities, and scripts. The functionalities provided in this project can also be directly invoked and integrated by Large Language Models (LLMs) through `matlab-mcp`.

## 📂 Project Structure

The repository currently contains the following main modules:

- **`detect-python-path`**: Skill for detecting the Python interpreter's absolute path via MATLAB pyenv, ensuring reliable terminal invocation of Python scripts. Avoids common pitfalls with conda or virtualenv interpreters.
- **`matlab-doc-injector`**: Tool for querying local MATLAB function documentation and injecting high-density Markdown into Agent context. Provides official function references (syntax, parameters, examples) when writing MATLAB code. **Requires Python 3.12+ and local MATLAB documentation download.**
- **`matlab-help-query`**: Skill for querying MATLAB function documentation using MATLAB CLI's help command. Provides quick access to function syntax, parameters, and usage examples. **No Python dependency, uses built-in MATLAB `help` command.**
- **`matlab-pdf-reader`**: Scripts and tools designed for reading, parsing, and processing PDF files within MATLAB. Supports full text extraction, page-specific extraction, metadata retrieval, and form data reading.
- **`matlab-table-reader`**: Utilities for efficiently reading, extracting, and manipulating various types of tabular data in MATLAB. Supports CSV, XLSX, XLS, and TXT formats with comprehensive data analysis capabilities.

## 🚀 Features

- **LLM Integration**: All skills are designed to be easily integrated with Large Language Models via `matlab-mcp`
- **Comprehensive Documentation**: Each skill includes detailed SKILL.md files with usage instructions, examples, and best practices
- **Cross-Platform Support**: Tools work across Windows, macOS, and Linux environments
- **Error Handling**: Built-in fallback mechanisms and error handling for robust operation

## 📊 Documentation Query Tools Comparison

This project provides two tools for querying MATLAB function documentation:

| Feature | `matlab-help-query` | `matlab-doc-injector` |
|---------|---------------------|----------------------|
| **Data Source** | MATLAB built-in `help` command | Local MATLAB HTML documentation |
| **Python Dependency** | ❌ No | ✅ Yes (Python 3.12+) |
| **Setup Required** | ❌ No (works out of box) | ✅ Yes (install + index build) |
| **Information Depth** | Basic (syntax, parameters, brief examples) | Comprehensive (full doc, examples, equations) |
| **Query Speed** | ~2-5s (MATLAB startup) | <10ms (cache hit), <500ms (cache miss) |
| **Output Format** | Plain text | High-density Markdown |
| **Best For** | Quick syntax checks, parameter lookup | Detailed reference, complex functions |

**When to use which:**
- Use **`matlab-help-query`** for: quick lookups, simple syntax checks, when Python is not available
- Use **`matlab-doc-injector`** for: comprehensive documentation, detailed examples, complex toolbox functions

## 📋 Prerequisites

- MATLAB R2024b or later (specific requirements vary by module)
- Python 3.12+ (for matlab-doc-injector)
- Required MATLAB toolboxes as specified in individual skill documentation

## 🛠️ Installation

Each skill can be installed and configured independently. Refer to the individual SKILL.md files in each module directory for specific installation instructions.
