function inspect_file(filename)
% INSPECT_FILE Inspect structure of a tabular data file
%   inspect_file(filename) displays information about the file structure
%   to help determine the best way to read it.
%
%   Example:
%       inspect_file('data.xlsx')
%       inspect_file('data.csv')

    fprintf('========================================\n');
    fprintf('File Inspection: %s\n', filename);
    fprintf('========================================\n\n');
    
    [~, ~, ext] = fileparts(filename);
    ext = lower(ext);
    
    try
        switch ext
            case {'.xlsx', '.xls'}
                inspect_excel(filename);
            case {'.csv', '.txt'}
                inspect_delimited(filename);
            otherwise
                fprintf('Unknown file type: %s\n', ext);
                fprintf('Attempting to detect format...\n\n');
                inspect_delimited(filename);
        end
    catch ME
        fprintf('Error inspecting file: %s\n', ME.message);
    end
end

function inspect_excel(filename)
    % Get sheet names
    sheet_names = sheetnames(filename);
    fprintf('Sheets found: %d\n', length(sheet_names));
    for i = 1:length(sheet_names)
        fprintf('  %d. %s\n', i, sheet_names{i});
    end
    fprintf('\n');
    
    % Inspect each sheet
    for i = 1:length(sheet_names)
        sheet_name = sheet_names{i};
        fprintf('--- Sheet: %s ---\n', sheet_name);
        
        try
            opts = detectImportOptions(filename, 'Sheet', sheet_name);
            fprintf('  Data range: %s\n', opts.DataRange);
            fprintf('  Variable names range: %s\n', opts.VariableNamesRange);
            fprintf('  Number of variables: %d\n', length(opts.VariableNames));
            fprintf('  Variable names:\n');
            for j = 1:length(opts.VariableNames)
                fprintf('    - %s (%s)\n', opts.VariableNames{j}, opts.VariableTypes{j});
            end
            
            % Preview
            preview_data = preview(filename, opts);
            fprintf('  Preview (first 5 rows):\n');
            disp(preview_data(1:min(5, height(preview_data)), :));
            
        catch ME
            fprintf('  Error reading sheet: %s\n', ME.message);
        end
        fprintf('\n');
    end
end

function inspect_delimited(filename)
    opts = detectImportOptions(filename);
    
    fprintf('Delimiter: %s\n', opts.Delimiter);
    fprintf('Number of variables: %d\n', length(opts.VariableNames));
    fprintf('Variable names:\n');
    for j = 1:length(opts.VariableNames)
        fprintf('  - %s (%s)\n', opts.VariableNames{j}, opts.VariableTypes{j});
    end
    
    % Preview
    preview_data = preview(filename, opts);
    fprintf('\nPreview (first 5 rows):\n');
    disp(preview_data(1:min(5, height(preview_data)), :));
end
