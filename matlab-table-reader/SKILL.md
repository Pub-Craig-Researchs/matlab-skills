---
name: matlab-table-reader
description: Read and analyze tabular data files (CSV, XLSX, XLS, TXT) using MATLAB. Use when the user needs to import data from spreadsheet files, perform statistical analysis, or process tabular data in a MATLAB environment. Trigger when the user mentions reading Excel files, CSV files, or any tabular data processing in MATLAB.
---

# MATLAB Table Data Reader

## Overview

This skill provides guidance for reading and analyzing tabular data files using MATLAB, including CSV, XLSX, XLS, and TXT formats.

## File Reading Methods

### CSV Files

```matlab
% Basic CSV reading
data = readtable('file.csv');

% With options
data = readtable('file.csv', 'Delimiter', ',', 'ReadVariableNames', true);

% Read as matrix (numeric data only)
data = readmatrix('file.csv');

% Read as cell array
data = readcell('file.csv');
```

### Excel Files (.xlsx, .xls)

```matlab
% Basic Excel reading
data = readtable('file.xlsx');

% Read specific sheet
data = readtable('file.xlsx', 'Sheet', 'Sheet1');

% Read specific range
data = readtable('file.xlsx', 'Range', 'A1:D100');

% Get sheet names
sheet_names = sheetnames('file.xlsx');

% Read with import options
opts = detectImportOptions('file.xlsx');
data = readtable('file.xlsx', opts);
```

### Text Files (.txt)

```matlab
% Delimited text file
data = readtable('file.txt');

% Fixed-width format
data = readtable('file.txt', 'FileType', 'text', 'Delimiter', '\t');

% Custom delimiter
data = readtable('file.txt', 'Delimiter', ';');
```

## Common Import Options

### Detect and Configure Import Options

```matlab
% Detect options
opts = detectImportOptions('file.xlsx');

% Preview data before importing
preview_data = preview('file.xlsx', opts);

% Configure variable types
opts.VariableTypes(2) = {'double'};
opts.VariableTypes(3) = {'datetime'};

% Preserve original variable names
opts.VariableNamingRule = 'preserve';

% Read with custom options
data = readtable('file.xlsx', opts);
```

### Date/Time Handling

```matlab
% Specify date format
data.Date = datetime(data.Date, 'InputFormat', 'dd-MMM-yyyy', 'Locale', 'en_US');

% Parse dates during import
opts = detectImportOptions('file.csv');
opts = setvaropts(opts, 'DateColumn', 'InputFormat', 'yyyy-MM-dd');
data = readtable('file.csv', opts);
```

## Data Analysis

### Basic Statistics

```matlab
% Summary statistics
summary(data);

% Descriptive statistics
stats = [mean(data.Var1), median(data.Var1), std(data.Var1), ...
         min(data.Var1), max(data.Var1)];

% Table of statistics
stats_table = table(mean(data.Var1), median(data.Var1), std(data.Var1), ...
    min(data.Var1), max(data.Var1), ...
    'VariableNames', {'Mean', 'Median', 'Std', 'Min', 'Max'});
```

### Data Filtering

```matlab
% Filter by date range
start_date = datetime(2020, 1, 1);
end_date = datetime(2024, 12, 31);
mask = (data.Date >= start_date) & (data.Date <= end_date);
filtered_data = data(mask, :);

% Filter by numeric condition
mask = data.Value > 0;
positive_data = data(mask, :);

% Remove missing values
clean_data = rmmissing(data);
```

## Best Practices

### 1. Always Check Data Structure First

```matlab
% Inspect data after reading
disp('Data size:'); disp(size(data));
disp('Column names:'); disp(data.Properties.VariableNames);
disp('First 5 rows:'); disp(head(data, 5));
disp('Data types:'); disp(varfun(@class, data, 'OutputFormat', 'cell'));
```

### 2. Handle Missing Data

```matlab
% Check for missing values
missing_count = sum(ismissing(data));

% Remove rows with any missing values
clean_data = rmmissing(data);

% Fill missing values
data.Var1 = fillmissing(data.Var1, 'linear');
```

### 3. Variable Name Handling

```matlab
% Access variables with spaces or special characters
value = data.('Variable Name');

% Rename variables
data.Properties.VariableNames{'OldName'} = 'NewName';
```

## Common Pitfalls

### Excel File Issues

- **Unicode errors**: Use `detectImportOptions` and `readtable` instead of `xlsread`
- **Multiple sheets**: Always check sheet names with `sheetnames()` first
- **Date formats**: Specify locale when parsing non-English dates
- **Merged cells**: May cause data misalignment; check data carefully

### CSV/TXT Issues

- **Delimiter detection**: Explicitly specify delimiter if auto-detection fails
- **Header rows**: Use `NumHeaderLines` option to skip headers
- **Encoding issues**: MATLAB uses system default encoding; convert files if needed

### Memory Considerations

```matlab
% For large files, read specific columns
opts = detectImportOptions('largefile.csv');
opts.SelectedVariableNames = {'Column1', 'Column2'};
data = readtable('largefile.csv', opts);

% Read in chunks (for very large files)
opts = detectImportOptions('largefile.csv');
opts.DataLines = [1 10000];  % Read first 10000 rows
data_chunk = readtable('largefile.csv', opts);
```

## Workflow Example

```matlab
% 1. Read data with proper options
opts = detectImportOptions('data.xlsx', 'Sheet', 'Monthly Data');
opts.VariableNamingRule = 'preserve';
data = readtable('data.xlsx', opts);

% 2. Clean and preprocess
valid_rows = ~isnan(data.Value);
data_clean = data(valid_rows, :);

% 3. Convert dates
data_clean.Date = datetime(data_clean.Date, 'InputFormat', 'dd-MMM-yyyy', 'Locale', 'en_US');

% 4. Filter by date range
start_date = datetime(1998, 1, 1);
end_date = datetime(2025, 6, 30);
mask = (data_clean.Date >= start_date) & (data_clean.Date <= end_date);
filtered_data = data_clean(mask, :);

% 5. Calculate statistics
obs = height(filtered_data);
mean_val = mean(filtered_data.Value);
median_val = median(filtered_data.Value);
stdev_val = std(filtered_data.Value);
min_val = min(filtered_data.Value);
max_val = max(filtered_data.Value);

% 6. Display results
fprintf('Obs: %d\n', obs);
fprintf('Mean: %.6f\n', mean_val);
fprintf('Median: %.6f\n', median_val);
fprintf('Stdev: %.6f\n', stdev_val);
fprintf('Min: %.6f\n', min_val);
fprintf('Max: %.6f\n', max_val);
```
