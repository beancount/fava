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

    // Toggle positions with checkboxes
    $('.table-filter input[type="checkbox"]').change(function() {
        var $this = $(this);
        var type = $this.attr('data-type');
        var shouldHide = $this.prop('checked');
        console.log(type, shouldHide);
        $('table.entry-table tr[data-type="' + type + '"]').toggle(shouldHide);
        $('table.entry-table tr[data-parent-type="' + type + '"]').toggle(shouldHide).toggleClass('hidden', !shouldHide);
    });
    $('.table-filter input[type="checkbox"]').each(function() { $(this).trigger('change'); });

    // Toggle legs by clicking on transaction/padding row
    $('table.entry-table tr[data-has-legs="True"]').click(function() {
        var hash = $(this).attr('data-hash');
        $('table.entry-table tr[data-parent-hash="' + hash + '"]').toggle(); // .toggleClass('hidden', shouldHide);
    });

    // Button "Hide/Show legs"
    $('input#toggle-legs').click(function(event) {
        event.preventDefault();
        var shouldHide = true;  // $(this).hasClass('hide-legs');
        $('table.entry-table tr[data-type="leg"]:not(.hidden)').toggle(!shouldHide).toggleClass('hidden', shouldHide);
        // $(this).toggleClass('hide-legs');
        // $(this).val(shouldHide ? 'Hide legs' : 'Show legs');
    });
});
