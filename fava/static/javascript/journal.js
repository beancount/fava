function initJournal() {
    // Toggle legs by clicking on transaction/padding row
    $('table.journal-table tr[data-type="transaction"]').click(function() {
        var $this = $(this);
        var hash = $this.attr('data-hash');
        $('table.journal-table tr[data-parent-hash="' + hash + '"]').toggle();
    });
    initJournalFilters();
}

function initJournalFilters() {
    // Toggle positions with checkboxes
    $('.table-filter input[type="checkbox"]').change(function() {
        var $this = $(this);
        var type = $this.attr('data-type');
        var shouldShow = $this.prop('checked');
        if (shouldShow) {
            $('table.journal-table tr[data-type="' + type + '"]').removeClass('hidden');
            $('table.journal-table tr.posting-' + type + '').removeClass('hidden-parent');
        } else {
            $('table.journal-table tr[data-type="' + type + '"]').addClass('hidden');
            $('table.journal-table tr.posting-' + type + '').addClass('hidden-parent');
        }
    });

    // Button "Hide/Show legs"
    $('input#toggle-legs').click(function(event) {
        event.preventDefault();
        var shouldShow = ($(this).val() == 'Show legs');
        if (shouldShow) {
            $('table.journal-table tr[data-type="posting"]').removeClass('hidden');
        } else {
            $('table.journal-table tr[data-type="posting"]').addClass('hidden');
        }
        $(this).val(shouldShow ? 'Hide legs' : 'Show legs');
    });

    // Button "Hide/Show metadata"
    $('input#toggle-metadata').click(function(event) {
        event.preventDefault();
        var shouldShow = ($(this).val() == 'Show metadata');
        if (shouldShow) {
            $('table.journal-table dl.metadata').removeClass('hidden');
        } else {
            $('table.journal-table dl.metadata').addClass('hidden');
        }
        $(this).val(shouldShow ? 'Hide metadata' : 'Show metadata');
    });
}

$(document).ready(function() {
    initJournal();
});
