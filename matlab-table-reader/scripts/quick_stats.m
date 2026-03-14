function stats = quick_stats(data, var_name)
% QUICK_STATS Calculate basic statistics for a numeric variable
%   stats = quick_stats(data, var_name) calculates Obs, Mean, Median,
%   Std, Min, Max for the specified variable in the table.
%
%   Example:
%       data = readtable('data.xlsx');
%       stats = quick_stats(data, 'Value')
%       stats = quick_stats(data, 2)  % Use column index

    if nargin < 2
        % Auto-detect first numeric column
        var_types = varfun(@class, data, 'OutputFormat', 'cell');
        numeric_idx = find(strcmp(var_types, 'double'), 1);
        if isempty(numeric_idx)
            error('No numeric columns found in data');
        end
        var_name = data.Properties.VariableNames{numeric_idx};
        fprintf('Using variable: %s\n', var_name);
    end
    
    % Get the data
    if isnumeric(var_name)
        values = data{:, var_name};
        var_name = data.Properties.VariableNames{var_name};
    else
        values = data.(var_name);
    end
    
    % Remove NaN values
    values = values(~isnan(values));
    
    if isempty(values)
        error('No valid numeric data found');
    end
    
    % Calculate statistics
    stats = struct();
    stats.Variable = var_name;
    stats.Obs = length(values);
    stats.Mean = mean(values);
    stats.Median = median(values);
    stats.Stdev = std(values);
    stats.Min = min(values);
    stats.Max = max(values);
    
    % Display results
    fprintf('\n========================================\n');
    fprintf('Statistics for: %s\n', var_name);
    fprintf('========================================\n');
    fprintf('Obs:    %d\n', stats.Obs);
    fprintf('Mean:   %.6f\n', stats.Mean);
    fprintf('Median: %.6f\n', stats.Median);
    fprintf('Stdev:  %.6f\n', stats.Stdev);
    fprintf('Min:    %.6f\n', stats.Min);
    fprintf('Max:    %.6f\n', stats.Max);
    fprintf('========================================\n');
end
