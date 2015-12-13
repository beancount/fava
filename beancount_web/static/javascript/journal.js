// http://stackoverflow.com/a/16315366
Handlebars.registerHelper('ifCond', function (v1, operator, v2, options) {
    switch (operator) {
        case '==':
            return (v1 == v2) ? options.fn(this) : options.inverse(this);
        case '===':
            return (v1 === v2) ? options.fn(this) : options.inverse(this);
        case '<':
            return (v1 < v2) ? options.fn(this) : options.inverse(this);
        case '<=':
            return (v1 <= v2) ? options.fn(this) : options.inverse(this);
        case '>':
            return (v1 > v2) ? options.fn(this) : options.inverse(this);
        case '>=':
            return (v1 >= v2) ? options.fn(this) : options.inverse(this);
        case '&&':
            return (v1 && v2) ? options.fn(this) : options.inverse(this);
        case '||':
            return (v1 || v2) ? options.fn(this) : options.inverse(this);
        default:
            return options.inverse(this);
    }
});

Handlebars.registerHelper('format_currency', function(number) {
    if (number) return number.toFixed(2);
});

Handlebars.registerHelper('context_url', function(hash) {
    return window.contextURL.replace("_REPLACE_ME_", hash);
});

Handlebars.registerHelper('account_url', function(accountName) {
    return window.accountURL.replace("_REPLACE_ME_", accountName);
});

$(document).ready(function() {
    var source   = $("#journal-template").html();
    var template = Handlebars.compile(source);
    var html    = template({ journal: window.journalAsJSON });
    $('.journal-table').append(html);
});
