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

    // Toggle all legs by clicking on "Hide/Show legs"
    $('.table-filter input#toggle-legs').click(function() {
        $('table.entry-table tr.leg').not('.hidden').toggle($(this).hasClass('hide-legs'));
        $(this).toggleClass('hide-legs');

        var text = $(this).prop('value');
        $(this).prop('value', text === 'Hide legs' ? 'Show legs' : 'Hide legs');

        return false;
    });
});



