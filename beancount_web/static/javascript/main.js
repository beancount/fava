$(document).ready(function() {
    $('.filter input').keyup(function() {
        var value = $(this).val();

        $(this).parents('.filter').find('li:not(:contains(' + value + '))').hide();
        $(this).parents('.filter').find('li:contains(' + value + ')').show();
    });

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

        var rowLevel = -1;

        $($(tableRow).prop('class').split(' ')).each(function(index, clazz) {
            if (clazz.startsWith('row-level-')) {
                rowLevel = parseInt(clazz.substring(10));
            }
        });

        return rowLevel;
    }

    var level = 1;
    $('table.tree-table tr').each(function() {
        var nextLevel = getLevel($(this).next());
        if (nextLevel <= level) { $(this).children().first().addClass('leaf'); }
        level = nextLevel;
    });

    $('table.tree-table tr td:first-child:not(.leaf) a.account').each(function() {
        $(this).append('<span class="expander"></span>');
    });

    $('table.tree-table span.expander').click(function() {
        var row = $(this).parents('tr');
        var level = getLevel(row);
        var hide = !$(this).hasClass('toggled');
        $(this).toggleClass('toggled');

        row.toggleClass('hides', hide);
        row = row.next();
        while (row.length > 0 && getLevel(row) > level) {
            row.toggleClass('hidden', hide);
            // console.log('row', row, hide, row.prop('class'));
            // row.children().first().toggleClass('hide', hide);
            row.find('span.expander').removeClass('toggled');
            row = row.next();
        }

        return false;
    });
});



