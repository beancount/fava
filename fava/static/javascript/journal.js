function initJournal() {
    // Toggle legs by clicking on transaction/padding row
    $('#journal-table tr[data-type="transaction"]').click(function() {
        var hash = $(this).attr('data-hash');
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
        $('#journal-table tr[data-type="' + type + '"]').toggleClass('hidden', !shouldShow);
        if (type == 'transaction') {
            $('#journal-table tr.posting').toggleClass('hidden-parent', !shouldShow);
        };
    });

    // Toggle transaction types with checkboxes
    $('#transaction-filters input[type="checkbox"]').change(function() {
        var $this = $(this);
        var type = $this.attr('data-type');
        var shouldShow = $this.prop('checked');
        $('#journal-table tr.' + type).toggleClass('hidden-type', !shouldShow);
        $('#journal-table tr.posting-' + type + '').toggleClass('hidden-parent-type', !shouldShow);
    });

    // Button "Hide/Show legs"
    $('input#toggle-legs').click(function(event) {
        event.preventDefault();
        var shouldShow = ($(this).val() == 'Show legs');
        $('#journal-table tr[data-type="posting"]').toggleClass('hidden', !shouldShow);
        $(this).val(shouldShow ? 'Hide legs' : 'Show legs');
    });

    // Button "Hide/Show metadata"
    $('input#toggle-metadata').click(function(event) {
        event.preventDefault();
        var shouldShow = ($(this).val() == 'Show metadata');
        $('#journal-table dl.metadata').toggleClass('hidden', !shouldShow);
        $(this).val(shouldShow ? 'Hide metadata' : 'Show metadata');
    });
}

module.exports.initJournal = initJournal;
