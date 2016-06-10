var Mousetrap = require('mousetrap');
require('mousetrap/plugins/bind-dictionary/mousetrap-bind-dictionary');

module.exports.global = function() {
    Mousetrap.bind({
        '?': function() { $('#keyboard-shortcuts.overlay-wrapper').show(); },
        'esc': function() { $('.overlay-wrapper').hide(); }
    }, 'keyup');

    // Filtering:
    Mousetrap.bind({
        'f t': function() {
            $('#time-filter').focus();
        },
        'f g': function() {
            $('#tag-filter').focus();
        },
        'f a': function() {
            $('#account-filter').focus();
        },
        'f p': function() {
            $('#name-filter').focus();
        },
    }, 'keyup');
};

module.exports.charts = function() {
    Mousetrap.bind({
        'ctrl+c': function() { $('#toggle-chart').click(); },
        'c':      function() {
            var next = $('#chart-labels label.selected').next();
            $('#chart-labels label').removeClass('selected');
            if (next.length) { next.click(); }
            else             { $('#chart-labels label:first-child').click(); }
        },
        'shift+c': function() {
            var prev = $('#chart-labels label.selected').prev();
            $('#chart-labels label').removeClass('selected');

            if (prev.length) { prev.click(); }
            else             { $('#chart-labels label:last-child').click(); }
        }
    }, 'keyup');
};

module.exports.journal = function() {
    Mousetrap.bind({
        'l':   function() { $('#toggle-legs').click(); },
        'm':   function() { $('#toggle-metadata').click(); },

        's o': function() { $('#filter-open').click(); },
        's c': function() { $('#filter-close').click(); },
        's t': function() { $('#filter-transaction').click(); },
        's b': function() { $('#filter-balance').click(); },
        's n': function() { $('#filter-note').click(); },
        's d': function() { $('#filter-document').click(); },
        's p': function() { $('#filter-pad').click(); },
        's q': function() { $('#filter-query').click(); },
        's shift+c': function() { $('#filter-custom').click(); },
        's shift+b': function() { $('#filter-budget').click(); },

        't c': function() { $('#filter-cleared').click(); },
        't p': function() { $('#filter-pending').click(); },
        't o': function() { $('#filter-other').click(); },
    }, 'keyup');
};
