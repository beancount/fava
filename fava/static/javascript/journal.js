module.exports.initJournal = function() {
    // Toggle legs by clicking on transaction/padding row
    $('#journal-table li.transaction').click(function() {
        $(this).find('.posting').toggleClass("hidden");
    });

    // Toggle entries with checkboxes
    $('#entry-filters input[type="checkbox"]').change(function() {
        var $this = $(this);
        var type = $this.attr('data-type');
        var shouldShow = $this.prop('checked');
        $('#journal-table li.' + type).toggleClass('hidden', !shouldShow);
    });

    // Toggle transaction types with checkboxes
    $('#transaction-filters input[type="checkbox"]').change(function() {
        var $this = $(this);
        var type = $this.attr('data-type');
        var shouldShow = $this.prop('checked');
        $('#journal-table li.' + type).toggleClass('hidden-type', !shouldShow);
    });

    // Button "Hide/Show legs"
    $('#toggle-legs').click(function(event) {
        event.preventDefault();
        var shouldShow = ($(this).val() == 'Show legs');
        $('#journal-table li.posting').toggleClass('hidden', !shouldShow);
        $(this).val(shouldShow ? 'Hide legs' : 'Show legs');
    });

    // Button "Hide/Show metadata"
    $('#toggle-metadata').click(function(event) {
        event.preventDefault();
        var shouldShow = ($(this).val() == 'Show metadata');
        $('#journal-table dl.metadata').toggleClass('hidden', !shouldShow);
        $(this).val(shouldShow ? 'Hide metadata' : 'Show metadata');
    });
}
