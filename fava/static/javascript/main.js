require('jquery-query-object');
require('jquery-stupid-table/stupidtable');

window.Mousetrap = require('mousetrap');
require('mousetrap/plugins/bind-dictionary/mousetrap-bind-dictionary');

require('./charts');

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

    // This fixes if there is a tree-balance, no balance and the row is not a parent.
    // Without this code the tree-balance would not be shown.
    $('table.tree-table tbody tr td:not(:first)').each(function(index, td) {
        if ($(td).find('span.balance').length == 0) {
            $(td).addClass('tree-balance-show');
        }
    });

    function getLevel(tableRow) {
        if ($(tableRow).length == 0) { return 0; }
        var rowLevel = parseInt($(tableRow).attr('data-level'));
        return rowLevel;
    }

    var level = 1;
    $('table.tree-table tr').each(function() {
        var nextLevel = getLevel($(this).next());
        if (nextLevel <= level) { $(this).children().first().addClass('leaf'); }
        level = nextLevel;
    });

    $('table.tree-table tr td:first-child:not(.leaf) a.account').each(function() {
        $(this).append('<span class="expander" title="Hold the Shift-key while clicking to expand all children"></span>');
    });

    function toggleTreeTableRow(row, hide, all) {
        var expander = row.find('span.expander');
        var level = getLevel(row);
        expander.toggleClass('toggled', hide);
        row.toggleClass('hides', hide);
        row = row.next();
        while (row.length > 0 && getLevel(row) > level) {
            if (hide == true) {
                row.toggleClass('hidden', hide);
                row.find('span.expander').removeClass('toggled');
            } else if (all == true) {
                row.toggleClass('hidden', hide);
            } else {
                    if (getLevel(row) == (level + 1)) {
                        row.toggleClass('hides', !hide);
                        row.toggleClass('hidden', hide);
                        row.find('span.expander').addClass('toggled');
                    }
            }

            row = row.next();
        }
    }

    $('table.tree-table span.expander').click(function(e) {
        var row = $(this).parents('tr');
        var all = e.shiftKey == true;
        toggleTreeTableRow(row, !row.hasClass('hides'), all);
        $('table.tree-table a.expand-all').addClass('not-fully-expanded');
        return false;
    });

    $('table.tree-table tr.hides').each(function() {
        toggleTreeTableRow($(this), true, false);
    });

    $('table.tree-table').on('click', 'a.expand-all.not-fully-expanded', function(e) {
        e.preventDefault();
        var $this = $(e.target);
        var row = $this.parents('table').find('tbody tr').first();
        toggleTreeTableRow(row, false, true);
        $this.removeClass('not-fully-expanded');
        return false;
    });

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
    if ($('.chart-labels').length) {
        Mousetrap.bind({
            'shift+c': function() { $('#toggle-chart').click(); },
            'c':       function() {
                var next = $('.chart-labels label.selected').next();
                $('.chart-labels label').removeClass('selected');
                if (next.length) { next.click(); }
                else             { $('.chart-labels label:first-child').click(); }
            },

        }, 'keyup');
    }

    // Options in transaction pages:
    if ($('.table-filter').length) {
        Mousetrap.bind({
            'l':   function() { $('#toggle-legs').click(); },
            's l': function() { $('#toggle-legs').click(); },
            'm':   function() { $('#toggle-metadata').click(); },
            's m': function() { $('#toggle-metadata').click(); },
            's o': function() { $('input#filter-open').click(); },
            's c': function() { $('input#filter-close').click(); },
            's t': function() { $('input#filter-transaction').click(); },
            's b': function() { $('input#filter-balance').click(); },
            's n': function() { $('input#filter-note').click(); },
            's d': function() { $('input#filter-document').click(); },
            's p': function() { $('input#filter-pad').click(); },
            's shift+p': function() { $('input#filter-padding').click(); }
        }, 'keyup');
    }

    Mousetrap.bind({
        '?': function() { $('.overlay-wrapper').show(); }
    }, 'keyup');

    $('.overlay-wrapper, .overlay-wrapper a.close').click(function(e) {
        if ($(e.target).hasClass('overlay-wrapper') || $(e.target).hasClass('close')) {
            e.preventDefault();
            $('.overlay-wrapper').hide();
        }
    });

    $('body').keyup(function(e) {
        if ($('.overlay-wrapper:visible').length && e.which == 27) {
            $('.overlay-wrapper').hide();
        }
    });
});



