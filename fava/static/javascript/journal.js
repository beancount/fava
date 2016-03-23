module.exports.initJournal = function() {
    // Toggle legs by clicking on transaction/padding row
    $('#journal-table li.transaction').click(function() {
        $(this).find('.posting').toggleClass("hidden");
    });

    // Toggle entries with checkboxes
    $('#entry-filters input').click(function() {
        event.preventDefault();
        var $this = $(this);
        var type = $this.attr('data-type');
        var shouldShow = $this.hasClass('inactive');
        $('#journal-table ' + type).toggleClass('hidden', !shouldShow);
        $this.toggleClass('inactive', !shouldShow);
    });
}
