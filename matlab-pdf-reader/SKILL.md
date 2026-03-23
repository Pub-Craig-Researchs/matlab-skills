---
name: matlab-pdf-reader
description: Extract and process text from PDF documents using MATLAB functions (extractFileText, pdfinfo, readPDFFormData). Use when the user needs to read, analyze, or extract content from PDF files in a MATLAB environment, or when PDF text is needed for further LLM analysis. Supports full text extraction, page-specific extraction, metadata retrieval, form data reading, and structured output generation.
---

# MATLAB PDF Reader

Read and process PDF documents using MATLAB's built-in text extraction capabilities. This skill leverages `extractFileText`, `pdfinfo`, and `readPDFFormData` to provide comprehensive PDF handling.

## Prerequisites

- **MATLAB R2017b+** with **Text Analytics Toolbox** (for `extractFileText`)
- **MATLAB R2018a+** for `readPDFFormData`
- `pdfinfo` available since R2021b

## Core Workflow

### Step 1: Validate the PDF file

Before extraction, always verify the file exists and is accessible:

```matlab
pdfPath = '/path/to/document.pdf';
assert(isfile(pdfPath), 'PDF file not found: %s', pdfPath);
```

### Step 2: Get PDF metadata (optional but recommended)

Use `pdfinfo` to understand the document structure before extraction:

```matlab
info = pdfinfo(pdfPath);
fprintf('Title: %s\n', info.Title);
fprintf('Pages: %d\n', info.NumPages);
fprintf('Author: %s\n', info.Author);
```

### Step 3: Extract text

Choose the appropriate extraction strategy:

| Scenario | Method | Code |
|----------|--------|------|
| Full document | Default | `str = extractFileText(pdfPath)` |
| Specific pages | Pages param | `str = extractFileText(pdfPath, 'Pages', 1:5)` |
| Better layout | article mode | `str = extractFileText(pdfPath, 'ExtractionMethod', 'article')` |
| All raw text | all-text mode | `str = extractFileText(pdfPath, 'ExtractionMethod', 'all-text')` |
| Encoding issues | Explicit encoding | `str = extractFileText(pdfPath, 'Encoding', 'UTF-8')` |

**Extraction method comparison:**

| ExtractionMethod | Best For | Notes |
|------------------|----------|-------|
| `'tree'` (default) | Structured documents | Preserves reading order from PDF tree |
| `'article'` | Academic papers, reports | Better paragraph/column handling |
| `'all-text'` | Maximum text coverage | Includes headers, footers, annotations |

### Step 4: Clean and format extracted text

```matlab
% Remove excessive whitespace
str = regexprep(str, '[ \t]+', ' ');
str = regexprep(str, '\n{3,}', '\n\n');
str = strtrim(str);
```

### Step 5: Read PDF form data (if applicable)

For PDFs containing fillable forms:

```matlab
try
    formData = readPDFFormData(pdfPath);
    fieldNames = fieldnames(formData);
    for i = 1:numel(fieldNames)
        fprintf('%s: %s\n', fieldNames{i}, string(formData.(fieldNames{i})));
    end
catch
    % Not a form PDF or no form fields — this is normal
end
```

## Recommended Extraction Strategies

### Academic papers

Academic PDFs often have multi-column layouts and mathematical notation. Use this approach:

```matlab
% Try 'article' first for better column handling
str = extractFileText(pdfPath, 'ExtractionMethod', 'article');

% If result is poor (garbled columns), fall back to 'tree'
if strlength(str) < 100
    str = extractFileText(pdfPath, 'ExtractionMethod', 'tree');
end

% If still poor, try 'all-text' as last resort
if strlength(str) < 100
    str = extractFileText(pdfPath, 'ExtractionMethod', 'all-text');
end
```

### Page-by-page extraction for large documents

For large PDFs, extract page by page to manage memory and enable targeted analysis:

```matlab
info = pdfinfo(pdfPath);
pages = cell(info.NumPages, 1);
for p = 1:info.NumPages
    pages{p} = extractFileText(pdfPath, 'Pages', p);
end
```

### Targeted section extraction

When only specific pages are needed (e.g., methodology section of a paper):

```matlab
% Extract pages 3-7 containing the methodology
str = extractFileText(pdfPath, 'Pages', 3:7);
```

## Complete Reference Template

Use `mcp_matlab_evaluate_matlab_code` to execute this pattern:

```matlab
pdfPath = '<ABSOLUTE_PATH_TO_PDF>';

% 1. Validate
assert(isfile(pdfPath), 'File not found: %s', pdfPath);

% 2. Metadata
try
    info = pdfinfo(pdfPath);
    fprintf('=== PDF Info ===\n');
    fprintf('Pages: %d\n', info.NumPages);
    fprintf('Title: %s\n', info.Title);
catch
    fprintf('pdfinfo unavailable (requires R2021b+)\n');
end

% 3. Extract with fallback chain
str = '';
methods = {'article', 'tree', 'all-text'};
for i = 1:numel(methods)
    try
        str = extractFileText(pdfPath, 'ExtractionMethod', methods{i});
        if strlength(str) > 100
            fprintf('Extracted with method: %s\n', methods{i});
            break;
        end
    catch e
        fprintf('Method %s failed: %s\n', methods{i}, e.message);
    end
end

% 4. Clean
str = regexprep(str, '[ \t]+', ' ');
str = regexprep(str, '\n{3,}', '\n\n');
str = strtrim(str);

% 5. Output (truncate if too long for display)
maxChars = 50000;
if strlength(str) > maxChars
    fprintf('Text length: %d chars (showing first %d)\n', strlength(str), maxChars);
    disp(extractBefore(str, maxChars + 1));
else
    disp(str);
end
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| File not found | Wrong path | Verify with `isfile(pdfPath)`, use absolute path |
| Encryption error | Password-protected | Add `'Password', 'xxx'` parameter |
| Empty output | Scanned/image PDF | OCR needed — MATLAB's `ocr()` from Computer Vision Toolbox |
| Garbled text | Wrong encoding | Try `'Encoding', 'UTF-8'` or `'ISO-8859-1'` |
| Toolbox missing | No Text Analytics Toolbox | Check with `ver('textanalytics')` |
| Poor layout | Multi-column PDF | Switch `ExtractionMethod` — try `'article'` or `'all-text'` |

## Tips

- **Always use absolute paths** for PDF files to avoid working directory issues
- **Prefer `'article'` extraction** for academic papers — it handles multi-column layouts better
- **Check text length** after extraction — very short output usually means the method failed
- **For LLM analysis**, extract to a string variable and pass it directly; avoid writing intermediate files unless the text exceeds context limits
- **For password-protected PDFs**: `extractFileText(pdfPath, 'Password', 'mypass')`
- **For specific pages**: `extractFileText(pdfPath, 'Pages', [1 3 5])` accepts non-contiguous pages
