define("ace/beancount/completer",["require","exports","module"], function(require, exports, module) {
"use strict";

var completionsAccounts = window.allAccounts.map(function (account) {
    return { name: account, value: account, score: 1, meta: "accounts" }
});
var completionsCommodities = window.allCommodities.map(function (commodity) {
    return { name: commodity, value: commodity, score: 2, meta: "commodities" }
});
var completionsDirectives = ['open', 'close', 'commodity', 'txn', 'balance', 'pad', 'note', 'document', 'price', 'event', 'option', 'plugin', 'include', 'query', "custom"].map(function (directive) {
    return { name: directive, value: directive, score: 3, meta: "directive" }
});
var completionsTags = window.allTags.map(function (tag) {
    return { name: '#' + tag, value: tag, score: 4, meta: "tags" }
});
var completions = completionsAccounts.concat(completionsCommodities, completionsDirectives);

var completionsCustom = ["budget", "fava-sidebar-link"].map(function(custom) {
    return { name: '"' + custom + '"', value: custom + '"', score: 5, meta: "custom" }
});
var completionsPeriods = ["daily", "weekly", "monthly", "yearly"].map(function(period) {
    return { name: '"' + period + '"', value: period + '"', score: 5, meta: "period" }
});

// Source: http://furius.ca/beancount/doc/options
var completionsOptions = ["title", "name_assets", "name_liabilities", "name_equity", "name_income", "name_expenses", "account_previous_balances",
                          "account_previous_earnings", "account_previous_conversions", "account_current_earnings", "account_current_conversions",
                          "account_rounding", "conversion_currency", "default_tolerance", "inferred_tolerance_multiplier", "infer_tolerance_from_cost",
                          "tolerance", "use_legacy_fixed_tolerances", "documents", "operating_currency", "render_commas", "plugin_processing_mode",
                          "plugin", "long_string_maxlines", "experiment_explicit_tolerances"].map(function(custom) {
    return { name: '"' + custom + '"', value: custom + '"', score: 5, meta: "option" }
});

var customDirectiveCompleter = function(line, pos, callback) {
    // 2016-01-01 custom "fava-sidebar-link" "title" "link"
    // 2016-01-01 custom "budget" Account "period" amount currency
    var parts = line.split(/\s+/);
    var completions = [];
    if (parts.length == 3) {
        completions = completionsCustom;
    } else if (parts.length > 2 && parts[2] == '"budget"') {
        if (parts.length == 4) {
            completions = completionsAccounts;
        } else if (parts.length == 5) {
            completions = completionsPeriods;
        }
    }
    callback(null, completions);
};

var optionDirectiveCompleter = function(line, pos, callback) {
    // option "key" "value"
    var parts = line.split(/\s+/);
    var completions = [];
    if (parts.length == 2) {
        completions = completionsOptions;
    }
    callback(null, completions);
};

var datedDirectiveCompleter = function() {
    var completionsDirectives = ['open', 'close', 'commodity', '*', 'txn', '!', '?', 'balance', 'pad', 'note', 'document', 'price', 'event', 'query', 'custom'].map(function (directive) {
        return { name: directive, value: directive, score: 3, meta: "directive" }
    });
    var completer = function() {
        var completers = arguments;
        return function(line, pos, callback) {
            var parts = line.split(/\s+/);
            if (completers.length >= parts.length) {
                callback(null, completers[parts.length - 1]);
            }
        };
    };
    var completers = {
        "open":         completer(null, null, completionsAccounts, completionsCommodities),
        "close":        completer(null, null, completionsAccounts),
        "commodity":    completer(null, null, completionsCommodities),
        "balance":      completer(null, null, completionsAccounts, [], completionsCommodities),
        "pad":          completer(null, null, completionsAccounts, completionsAccounts),
        "note":         completer(null, null, completionsAccounts),
        "document":     completer(null, null, completionsAccounts),
        "price":        completer(null, null, completionsCommodities, [], completionsCommodities),
        "custom":       customDirectiveCompleter
    };
    return function(line, pos, callback) {
        if (/^[0-9]{4}\-[0-9]{2}\-[0-9]{2}\s+/.test(line)) {
            var completions = [];
            var parts = line.split(/\s+/);
            if (parts.length == 2) {
                callback(null, completionsDirectives);
            } else if (parts.length > 2 && parts[1] in completers) {
                completers[parts[1]](line, pos, callback);
            } else {
                return false;
            }
            return true;
        }
        return false;
    }
}();

var undatedDirectiveCompleter = function() {
    var completionsDirectives = ['option', 'plugin', 'include'].map(function (directive) {
        return { name: directive, value: directive, score: 3, meta: "directive" }
    });
    var completer = function() {
        var completers = arguments;
        return function(line, pos, callback) {
            var parts = line.split(/\s+/);
            if (completers.length >= parts.length) {
                callback(null, completers[parts.length - 1]);
            }
        };
    };
    var completers = {
        "option": optionDirectiveCompleter,
    };
    return function(line, pos, callback) {
        var parts = line.split(/\s+/);
        if (parts.length == 0) {
            callback(null, completionsDirectives);
        } else if (parts.length > 1 && parts[0] in completers) {
            completers[parts[0]](line, pos, callback);
        } else {
            return false;
        }
        return true;
    }
}();

var beancountCompleter = {
    getCompletions: function(editor, session, pos, prefix, callback) {
        if (prefix.length === 0) { callback(null, []); return }
        var line = editor.session.getLine(pos.row);
        if (prefix == '#') { callback(null, completionsTags); return }
        if (datedDirectiveCompleter(line, pos, callback)) return;
        if (undatedDirectiveCompleter(line, pos, callback)) return;
        if (line.indexOf('#') > -1) { callback(null, completionsTags); return }
        if (line.indexOf('"') > -1) { callback(null, []); return }
        callback(null, completions);
    }
}

exports.beancountCompleter = beancountCompleter;
});
