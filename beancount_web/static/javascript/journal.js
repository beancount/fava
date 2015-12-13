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
    if (number) return formatCurrency(number);
});

Handlebars.registerHelper('context_url', function(hash) {
    return window.contextURL.replace("_REPLACE_ME_", hash);
});

Handlebars.registerHelper('account_url', function(accountName) {
    return window.accountURL.replace("_REPLACE_ME_", accountName);
});

Handlebars.registerHelper('ifShowChangeAndBalance', function(unused, options) {
    return window.journalShowChangeAndBalance ? options.fn(this) : options.inverse(this);
});

$(document).ready(function() {
    var source   = $("#journal-template").html();
    var template = Handlebars.compile(source);
    var html    = template({ journal: window.journalAsJSON });
    $('.journal-table').html(html);

    function toggle_journal_types() {
        $('.table-filter input[type="checkbox"]').each(function() {
            var type = $(this).prop('id').substring(7);
            $('table.entry-table tr.' + type).toggle($(this).prop('checked'));
            $('table.entry-table tr.leg-' + type).toggle($(this).prop('checked'));
            $('table.entry-table tr.leg-' + type).toggleClass('hidden', !$(this).prop('checked'));
        });
    }

    // Toggle positions with checkboxes
    $('.table-filter input[type="checkbox"]').change(function() {
        toggle_journal_types();
    });
    toggle_journal_types();

    // Toggle legs by clicking on transaction/padding row
    $('table.entry-table tr.transaction td, table.entry-table tr.padding td').click(function() {
        $.each($(this).parents('tr').prop('class').split(' '), function(index, clazz) {
            if (clazz.startsWith('journal-entry-')) {
                $('table.entry-table tr.leg.' + clazz).toggle();
                $('table.entry-table tr.leg.' + clazz).toggleClass('hidden');
            }
        });
    });

    // Button "Hide legs"
    $('input#toggle-legs').click(function(event) {
        event.preventDefault();
        var shouldHide = $(this).hasClass('hide-legs');
        $('table.entry-table tr').each(function() {
            $.each($(this).prop('class').split(' '), function(index, clazz) {
                if (clazz.startsWith('journal-entry-')) {
                    $('table.entry-table tr.leg.' + clazz).toggle(shouldHide);
                    $('table.entry-table tr.leg.' + clazz).toggleClass('hidden', shouldHide);
                }
            });
        });
        $(this).toggleClass('hide-legs');
    });
});
