# MATLAB Skills

This is a repository that archives personal MATLAB skills, utilities, and scripts. The functionalities provided in this project can also be directly invoked and integrated by Large Language Models (LLMs) through `matlab-mcp`.

## 📂 Project Structure

The repository currently contains the following main modules:

- **`detect-python-path`**: Skill for detecting the Python interpreter's absolute path via MATLAB pyenv, ensuring reliable terminal invocation of Python scripts. Avoids common pitfalls with conda or virtualenv interpreters.
- **`matlab-doc-injector`**: Tool for querying local MATLAB function documentation and injecting high-density Markdown into Agent context. Provides official function references (syntax, parameters, examples) when writing MATLAB code.
- **`matlab-pdf-reader`**: Scripts and tools designed for reading, parsing, and processing PDF files within MATLAB. Supports full text extraction, page-specific extraction, metadata retrieval, and form data reading.
- **`matlab-table-reader`**: Utilities for efficiently reading, extracting, and manipulating various types of tabular data in MATLAB. Supports CSV, XLSX, XLS, and TXT formats with comprehensive data analysis capabilities.

## 🚀 Features

- **LLM Integration**: All skills are designed to be easily integrated with Large Language Models via `matlab-mcp`
- **Comprehensive Documentation**: Each skill includes detailed SKILL.md files with usage instructions, examples, and best practices
- **Cross-Platform Support**: Tools work across Windows, macOS, and Linux environments
- **Error Handling**: Built-in fallback mechanisms and error handling for robust operation

## 📋 Prerequisites

- MATLAB R2024b or later (specific requirements vary by module)
- Python 3.12+ (for matlab-doc-injector)
- Required MATLAB toolboxes as specified in individual skill documentation

## 🛠️ Installation

Each skill can be installed and configured independently. Refer to the individual SKILL.md files in each module directory for specific installation instructions.
