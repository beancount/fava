require('jquery-query-object');
require('jquery-stupid-table/stupidtable');

window.Mousetrap = require('mousetrap');
require('mousetrap/plugins/bind-dictionary/mousetrap-bind-dictionary');

require('./charts');
var journal = require('./journal');
var treeTable = require('./tree-table');

// expose jquery to global context
window.$ = $

$(document).ready(function() {
    $("table.sortable").stupidtable();

    $('.filter input').keyup(function() {
        var $this = $(this);
        var value = $this.val();
        $(this).parents('.filter').find('li.suggestion').toggle(value == '');
        $(this).parents('.filter').find("li[data-filter*='" + value.toLowerCase() + "']").show();
    });

    $('.filter#filter-time input').keyup(function(e) {
        var $this = $(this);
        var code = e.which;
        if (code == 13) {
            e.preventDefault();
            window.location.href = location.pathname + ($.query.set('time', $this.val()));
        }
    });

    // Tree-expanding
    if ($('table.tree-table').length) {
        treeTable.initTreeTable();
    };

    // Journal
    if ($('#journal-table').length) {
        journal.initJournal();
    };

    // Keyboard shortcuts

    // Filtering:
    $("body").click(function(){
        $("ul.topmenu li").removeClass("opened");
    });

    $("ul.topmenu li").click(function(e){
        e.stopPropagation();
    });

    $('ul.topmenu input[type=search]').keyup(function(e) {
        if (e.which == 27) {
            $(this).blur();
            $(this).parents('li').removeClass("opened");
        }
    });

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
            't u': function() { $('#filter-uncleared').click(); },
            't p': function() { $('#filter-padding').click(); },
            't s': function() { $('#filter-summarize').click(); },
            't t': function() { $('#filter-transfer').click(); },
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
