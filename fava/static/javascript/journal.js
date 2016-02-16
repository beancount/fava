function initJournal() {
    // Toggle legs by clicking on transaction/padding row
    $('#journal-table tr[data-type="transaction"]').click(function() {
        var $this = $(this);
        var hash = $this.attr('data-hash');
        $('#journal-table tr[data-parent-hash="' + hash + '"]').toggleClass("hidden");
    });
    initJournalFilters();
}

function initJournalFilters() {
    // Toggle entries with checkboxes
    $('#entry-filters input[type="checkbox"]').change(function() {
        var $this = $(this);
        var type = $this.attr('data-type');
        var shouldShow = $this.prop('checked');
        if (shouldShow) {
            $('#journal-table tr[data-type="' + type + '"]').removeClass('hidden');
            $('#journal-table tr.posting-' + type + '').removeClass('hidden-parent');
        } else {
            $('#journal-table tr[data-type="' + type + '"]').addClass('hidden');
            $('#journal-table tr.posting-' + type + '').addClass('hidden-parent');
        }
    });

    // Toggle transaction types with checkboxes
    $('#transaction-filters input[type="checkbox"]').change(function() {
        var $this = $(this);
        var type = $this.attr('data-type');
        var shouldShow = $this.prop('checked');
        if (shouldShow) {
            $('#journal-table tr.' + type).removeClass('hidden-type');
            $('#journal-table tr.posting-' + type + '').removeClass('hidden-parent-type');
        } else {
            $('#journal-table tr.' + type).addClass('hidden-type');
            $('#journal-table tr.posting-' + type + '').addClass('hidden-parent-type');
        }
    });

    // Button "Hide/Show legs"
    $('input#toggle-legs').click(function(event) {
        event.preventDefault();
        var shouldShow = ($(this).val() == 'Show legs');
        if (shouldShow) {
            $('#journal-table tr[data-type="posting"]').removeClass('hidden');
        } else {
            $('#journal-table tr[data-type="posting"]').addClass('hidden');
        }
        $(this).val(shouldShow ? 'Hide legs' : 'Show legs');
    });

    // Button "Hide/Show metadata"
    $('input#toggle-metadata').click(function(event) {
        event.preventDefault();
        var shouldShow = ($(this).val() == 'Show metadata');
        if (shouldShow) {
            $('#journal-table dl.metadata').removeClass('hidden');
        } else {
            $('#journal-table dl.metadata').addClass('hidden');
        }
        $(this).val(shouldShow ? 'Hide metadata' : 'Show metadata');
    });
}

$(document).ready(function() {
    initJournal();
});
