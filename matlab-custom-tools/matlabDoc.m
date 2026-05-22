function result = matlabDoc(query)
    % Get MATLAB documentation by exact function name or keyword search.
    % Tries help (exact match) first; falls back to lookfor (keyword search)
    % if no exact match is found. Returns "Not found" if both fail.
    %
    %   result = matlabDoc(query)
    %
    %   query  - Function name or keyword to search (1,1) string
    %            MUST be a single identifier / single keyword with NO whitespace.

    arguments
        query (1,1) string
    end

    % Guard: reject multi-token (whitespace-separated) queries.
    % matlabDoc wraps help/lookfor, both of which accept a SINGLE identifier
    % or keyword only. A query like "trainingOptions DispatchInBackground
    % PreprocessingEnvironment" silently returns Not found because help treats
    % it as one missing name and lookfor searches the full substring.
    % Tell the caller explicitly instead of returning a confusing miss.
    trimmed = strtrim(query);
    if ~isempty(regexp(trimmed, '\s', 'once'))
        result = "Not found: " + query + newline + ...
            "(matlabDoc accepts ONE function/class/method name or ONE keyword per call. " + ...
            "To look up multiple topics, call this tool in parallel with one query each, " + ...
            "e.g. query='trainingOptions' and query='PreprocessingEnvironment' as two separate calls.)";
        return;
    end

    escaped = strrep(trimmed, "'", "''");

    % Step 1: try exact help lookup
    cmd = sprintf("help('%s')", escaped);
    helpOutput = strtrim(evalc(cmd));

    if ~isempty(helpOutput) && ~contains(helpOutput, "not found", "IgnoreCase", true) && ~contains(helpOutput, "未找到")
        result = string(helpOutput);
        result = cleanOutput(result);
        result = appendOverloads(result, trimmed);
        return;
    end

    % Step 2: fallback to keyword search via lookfor
    cmd = sprintf("lookfor('%s')", escaped);
    lookforOutput = strtrim(evalc(cmd));

    if ~isempty(lookforOutput) && ~contains(lookforOutput, "not found", "IgnoreCase", true) && ~contains(lookforOutput, "未找到")
        result = string(lookforOutput);
        result = cleanOutput(result);
    else
        result = "Not found: " + query;
    end
end

function out = cleanOutput(s)
    % Strip HTML tags and boilerplate footer lines
    out = regexprep(s, "<a [^>]*>(.*?)</a>", "$1");
    out = regexprep(out, "<strong>([^<]*)</strong>", "$1");
    out = regexprep(out, "\n\s*已在 [^\n]*中引入", "");
    out = regexprep(out, "\n\s*[^\n]*的文档", "");
    out = regexprep(out, "\n\s*[^\n]*的其他用法", "");
end

function out = appendOverloads(s, funcName)
    % If funcName has multiple implementations, list them with queryable paths
    w = which(funcName, "-all");
    if numel(w) <= 1
        out = s;
        return;
    end
    parts = strings(numel(w), 1);
    for i = 1:numel(w)
        parts(i) = formatOverload(w{i}, funcName);
    end
    parts = unique(parts);
    out = s + newline + "重载版本:";
    for i = 1:numel(parts)
        out = out + newline + "  " + parts(i);
    end
end

function label = formatOverload(whichPath, funcName)
    % Format a which result as an actionable label
    tokens = regexp(string(whichPath), "@(\w+)", "tokens", "once");
    if ~isempty(tokens)
        className = tokens{1};
        if contains(whichPath, "built-in")
            label = className;           % built-in type overload, just show type
        else
            label = className + "/" + funcName;  % class method, queryable
        end
    elseif contains(whichPath, "built-in")
        label = "built-in";
    else
        label = "other";
    end
end
