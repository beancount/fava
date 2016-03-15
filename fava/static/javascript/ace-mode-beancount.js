define("ace/mode/beancount_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;
var SqlHighlightRules = require("ace/mode/sql_highlight_rules").SqlHighlightRules;

var BeancountHighlightRules = function() {

    this.$rules = {
        start: [{
            token: "comment.line.beancount",
            regex: /;.*/,
            comment: "Commented text"
        }, {
            token: "comment.line.shebang",
            regex: /^#!.*/,
            comment: "Shebangs"
        }, {
            token: "section.line.beancount",
            regex: /^\*+ .+$/,
            comment: "Section marker"
        }, {
            token: "string.quoted.triple.beancount",
            regex: /"""/,
            comment: "Multi-line strings (embedded SQL)",
            next: "sql-start"
        }, {
            token: "string.quoted.double.beancount",
            regex: /"[^"]*"/,
            comment: "strings"
        }, {
            token: [
                "text",
                "constant.language.beancount",
                "punctuation.separator.beancount"
            ],
            regex: /(\s)([A-Z][A-Za-z0-9\-]+)(:)/,
            comment: "Root Accounts"
        }, {
                token: [
                    "punctuation.separator.beancount",
                    "variable.account.beancount"
                ],
                regex: /([:]?)([A-Z][A-Za-z0-9\-]+)/,
            comment: "Accounts"
        }, {
            token: [
                "text",
                "constant.language.beancount",
                "punctuation.separator.beancount"
            ],
            regex: /(\s)([a-z][A-Za-z0-9\-\_]+)(:)/,
            comment: "Metadata"
        }, {
            token: [
                "support.function.directive.option.beancount",
                "meta.directive.option.beancount",
                "support.variable.language.option.beancount",
                "meta.directive.option.beancount",
                "support.class.option.beancount",
                "meta.directive.option.beancount"
            ],
            regex: /^(option)(\s*)(\".*\")(\s*)(\".*\")(\s*)/,
            comment: "Option directives"
        }, {
            token: "keyword.operator.directive.beancount",
            regex: /^(?:poptag|pushtag)\s/,
            comment: "Directives (no date)"
        }, {
            token: "variable.other.currency.beancount",
            regex: /\s[A-Z][A-Z0-9\'\.\_\-]{0,10}[A-Z0-9][\,?|\s]/,
            comment: "Currencies"
        }, {
            token: [
                "constant.numeric.date.year.beancount",
                "text",
                "constant.numeric.date.month.beancount",
                "text",
                "constant.numeric.date.day.beancount",
                "text",
                "support.function.directive.beancount"
            ],
            regex: /([0-9]{4})(\-)([0-9]{2})(\-)([0-9]{2})(\s)(open|close|pad|balance|note|price|event|document|commodity|query)/,
            comment: "Dated directives"
        }, {
            token: [
                "constant.numeric.date.year.beancount",
                "text",
                "constant.numeric.date.month.beancount",
                "text",
                "constant.numeric.date.day.beancount",
                "support.function.directive.beancount",
                "text"
            ],
            regex: /([0-9]{4})(\-)([0-9]{2})(\-)([0-9]{2})((?:\stxn)?)(\s)/,
            comment: "Transactions"
        }, {
            token: "keyword.other.beancount",
            regex: /\!\s/,
            comment: "flag"
        }, {
            token: "keyword.operator.assignment.beancount",
            regex: /\@/,
            comment: "Price assignment"
        }, {
            token: "keyword.operator.assignment.beancount",
            regex: /\{/,
            comment: "cost assignment"
        }, {
            token: ["text", "string.unquoted.tag.beancount"],
            regex: /(#)([A-Za-z0-9\-_\/.]+)/,
            comment: "Tags and links"
        }, {
            token: ["text", "string.unquoted.link.beancount"],
            regex: /(\^)([A-Za-z0-9\-_\/.]+)/,
            comment: "Links"
        }, {
            token: [
                "keyword.operator.modifier.beancount",
                "constant.numeric.currency.beancount"
            ],
            regex: /([\-|\+]?)([\d]+[\.]?[\d]*)/,
            comment: "numbers"
        }, {
            token: "invalid.illegal.unrecognized.beancount",
            regex: /[^\s}]/,
            comment: "Illegal"
        }],
        "#account-names": [{
            token: "text",
            regex: /[A-Z][A-Za-z0-9\-]+/
        }],
        "#dates": [{
            token: [
                "constant.numeric.date.year.beancount",
                "punctuation.separator.beancount",
                "constant.numeric.date.month.beancount",
                "punctuation.separator.beancount",
                "constant.numeric.date.day.beancount"
            ],
            regex: /([0-9]{4})(\-)([0-9]{2})(\-)([0-9]{2})/
        }],
        "#numbers": [{
            token: [
                "keyword.operator.modifier.beancount",
                "constant.numeric.currency.beancount"
            ],
            regex: /([\-|\+]?)([\d]+[\.]?[\d]*)/
        }, {
            token: "comment.line.beancount",
            regex: /\*.*/,
            comment: "Commented text"
        }]
    }

    this.embedRules(SqlHighlightRules, "sql-", [{
        token: "string.quoted.triple.beancount",
        regex: /"""/,
        comment: "Multi-line strings",
        next: "start"
    }]);

    this.normalizeRules();
};

BeancountHighlightRules.metaData = {
    fileTypes: ["beancount"],
    name: "Beancount",
    scopeName: "source.beancount"
}


oop.inherits(BeancountHighlightRules, TextHighlightRules);

exports.BeancountHighlightRules = BeancountHighlightRules;
});

define("ace/mode/folding/orgstyle",["require","exports","module","ace/lib/oop","ace/range","ace/mode/folding/fold_mode"], function(require, exports, module) {
"use strict";

var oop = require("../../lib/oop");
var Range = require("../../range").Range;
var BaseFoldMode = require("./fold_mode").FoldMode;

var FoldMode = exports.FoldMode = function() {};
oop.inherits(FoldMode, BaseFoldMode);

(function() {
    this.foldingStartMarker = /^(\*+) (.+)$/;
    this.foldingStopMarker;

    this._getFoldWidgetBase = this.getFoldWidget;
    this.getFoldWidget = function(session, foldStyle, row) {
        var line = session.getLine(row);

        if (!this.foldingStartMarker.test(line)) {
            return "";
        }

        var fw = this._getFoldWidgetBase(session, foldStyle, row);

        if (!fw && this.foldingStartMarker.test(line))
            return "start";

        return fw;
    };

    this.getFoldWidgetRange = function(session, foldStyle, row) {
        var line = session.getLine(row);

        var match = line.match(this.foldingStartMarker);
        if (match) {
            console.log(match);
            var startColumn = line.length;
            var maxRow = session.getLength();
            var startRow = row;
            var level = match[1].length

            while (++row < maxRow) {
                line = session.getLine(row);
                var m = this.foldingStartMarker.exec(line);
                if (!m) continue;
                if (m[1].length <= level) break;
            }

            var endRow = row;
            if (endRow > startRow) {
                if (endRow < maxRow) endRow--;
                return new Range(startRow, startColumn, endRow, line.length);
            }
        }
    };

}).call(FoldMode.prototype);

});

define("ace/mode/beancount",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/beancount_highlight_rules","ace/mode/folding/cstyle"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var BeancountHighlightRules = require("./beancount_highlight_rules").BeancountHighlightRules;
var FoldMode = require("./folding/orgstyle").FoldMode;

var Mode = function() {
    this.HighlightRules = BeancountHighlightRules;
    this.foldingRules = new FoldMode();
};
oop.inherits(Mode, TextMode);

(function() {
    this.$id = "ace/mode/beancount"
}).call(Mode.prototype);

exports.Mode = Mode;
});
