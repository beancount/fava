var Handlebars = require('handlebars');

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

Handlebars.registerHelper('format_currency', function (number) {
    if (isNumber(number)) return formatCurrency(number);
});

Handlebars.registerHelper('context_url', function (hash) {
    return window.contextURL.replace("REPLACEME", hash);
});

Handlebars.registerHelper('account_url', function (accountName) {
    return window.accountURL.replace("REPLACEME", accountName);
});

Handlebars.registerHelper('query_url', function (queryName) {
    return window.queryURL.replace("REPLACEME", queryName);
});

Handlebars.registerHelper('tag_url', function (tagName) {
    return window.tagURL.replace("REPLACEME", tagName);
});

Handlebars.registerHelper('document_url', function (documentPath) {
    return window.documentURL.replace("REPLACEME", encodeURIComponent(documentPath));
});

Handlebars.registerHelper('ifHasElements', function (object, options) {
    return Object.keys(object).length > 0 ? options.fn(this) : options.inverse(this);
});

Handlebars.registerHelper('ifShowChangeAndBalance', function (unused, options) {
    return window.journalShowChangeAndBalance ? options.fn(this) : options.inverse(this);
});

Handlebars.registerHelper('ifShowLegs', function (unused, options) {
    return window.journalShowLegs ? options.fn(this) : options.inverse(this);
});

Handlebars.registerHelper('ifShowMetadata', function (unused, options) {
    return window.journalShowMetadata ? options.fn(this) : options.inverse(this);
});

Handlebars.registerHelper('ifShowType', function (unused, options) {
    return $.inArray(
            options.data.root.journal[options.data.index].meta.type,
            window.journalShowTypes
        ) > -1 ? options.fn(this) : options.inverse(this);
});

var tableTemplate = Handlebars.compile($("#journal-table-template").html());
var legTemplate = Handlebars.compile($("#journal-leg-template").html());
Handlebars.registerPartial('legPartialTemplate', legTemplate)

function drawJournal() {
    var html = tableTemplate({ journal: window.journalAsJSON });
    $('.journal-table').html(html);

    // Toggle legs by clicking on transaction/padding row
    $('table.journal-table tr[data-has-legs="True"]').click(function() {
        var $this = $(this);
        var hash = $this.attr('data-hash');

        if ($this.hasClass('display-legs')) {
            $('table.journal-table tr[data-parent-hash="' + hash + '"]').remove();
        } else {
            var journalEntry = {};
            $.each(window.journalAsJSON, function(index, entry) {
                if (entry.hash == hash) {
                    journalEntry = entry;
                    return;
                }
            });

            if (journalEntry) {
                var html = legTemplate({ journalEntry: journalEntry, legs: journalEntry.legs, hash: journalEntry.hash  });
                $this.after(html);
            } else {
                console.warn("Hash not found", hash, window.journalAsJSON);
            }
        }

        $this.toggleClass('display-legs');
    });
}

function initJournalFilters() {
    // Toggle positions with checkboxes
    $('.table-filter input[type="checkbox"]').change(function() {
        var $this = $(this);
        var type = $this.attr('data-type');
        var shouldShow = $this.prop('checked');

        if (shouldShow && $.inArray(type, window.journalShowTypes) == -1) {
            window.journalShowTypes.push(type);
        } else if ($.inArray(type, window.journalShowTypes) > -1) {
            window.journalShowTypes.splice($.inArray(type, window.journalShowTypes), 1);
        }

        drawJournal();
    });

    // Button "Hide/Show legs"
    $('input#toggle-legs').click(function(event) {
        event.preventDefault();
        var shouldShow = !window.journalShowLegs;
        $('table.journal-table tr[data-type="leg"]:not(.hidden)').toggle(shouldShow).toggleClass('hidden', !shouldShow);
        window.journalShowLegs = !window.journalShowLegs;
        drawJournal();
        $(this).val(shouldShow ? 'Hide legs' : 'Show legs');
    });

    // Button "Hide/Show metadata"
    $('input#toggle-metadata').click(function(event) {
        event.preventDefault();
        var shouldShow = !window.journalShowMetadata;
        $('table.journal-table dl.metadata').toggle(shouldShow).toggleClass('hidden', !shouldShow);
        window.journalShowMetadata = !window.journalShowMetadata;
        $(this).val(shouldShow ? 'Hide metadata' : 'Show metadata');
    });
}

$(document).ready(function() {
    if (window.journalAsJSON != undefined) {
        drawJournal();
        initJournalFilters();
    } else if (window.journalURL != undefined) {
        $.get(window.journalURL)
        .done(function(responseData) {
            window.journalAsJSON = responseData.data;
            drawJournal();
            initJournalFilters();
        });
    }
});
