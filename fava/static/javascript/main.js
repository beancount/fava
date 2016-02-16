require('jquery-query-object');
require('jquery-stupid-table/stupidtable');

window.Mousetrap = require('mousetrap');
require('mousetrap/plugins/bind-dictionary/mousetrap-bind-dictionary');

require('./charts');
var filters = require('./filters');
var journal = require('./journal');
var treeTable = require('./tree-table');

// expose jquery to global context
window.$ = $

$(document).ready(function() {
    $("table.sortable").stupidtable();

    // Setup filters form
    filters.initFilters();

    // Tree-expanding
    if ($('table.tree-table').length) {
        treeTable.initTreeTable();
    };

    // Journal
    if ($('#journal-table').length) {
        journal.initJournal();
    };

    // Keyboard shortcuts

    // Jumping through charts
    if ($('#chart-labels').length) {
        Mousetrap.bind({
            'shift+c': function() { $('#toggle-chart').click(); },
            'c':       function() {
                var next = $('#chart-labels label.selected').next();
                $('#chart-labels label').removeClass('selected');
                if (next.length) { next.click(); }
                else             { $('#chart-labels label:first-child').click(); }
            },

        }, 'keyup');
    }

    // Options in transaction pages:
    if ($('#entry-filters').length) {
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
    }

    Mousetrap.bind({
        '?': function() {
            $('#overlay-wrapper').show();
            $('#overlay-wrapper, #overlay-wrapper a.close').click(function(e) {
                e.preventDefault();
                $('#overlay-wrapper').hide();
            });
        },
        'esc': function() { $('#overlay-wrapper').hide(); }
    }, 'keyup');

});
