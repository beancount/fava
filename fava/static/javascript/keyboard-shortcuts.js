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
            $('ul.topmenu>li').removeClass('opened');
            $('ul.topmenu>li:nth-child(1)').toggleClass('opened').find('input[type=search]').focus();
        },
        'f g': function() {
            $('ul.topmenu>li').removeClass('opened');
            $('ul.topmenu>li:nth-child(2)').toggleClass('opened').find('input[type=search]').focus();
        },
        'f c': function() {
            $('ul.topmenu>li').removeClass('opened');
            $('ul.topmenu>li:nth-child(3)').toggleClass('opened').find('input[type=search]').focus();
        },
        'f p': function() {
            $('ul.topmenu>li').removeClass('opened');
            $('ul.topmenu>li:nth-child(4)').toggleClass('opened').find('input[type=search]').focus();
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

        't c': function() { $('#filter-cleared').click(); },
        't p': function() { $('#filter-pending').click(); },
        't shift+p': function() { $('#filter-padding').click(); },
        't s': function() { $('#filter-summarize').click(); },
        't t': function() { $('#filter-transfer').click(); },
        't o': function() { $('#filter-other').click(); },
    }, 'keyup');
};
