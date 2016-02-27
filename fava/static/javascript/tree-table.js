function initTreeTable() {
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
            if (hide === true) {
                row.toggleClass('hidden', hide);
                row.find('span.expander').removeClass('toggled');
            } else if (all === true) {
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
        var all = e.shiftKey === true;
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
}

module.exports.initTreeTable = initTreeTable;
