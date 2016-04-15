const queryString = require('query-string');

module.exports.initJournal = function() {
    // Toggle legs by clicking on transaction/padding row
    $('#journal-table li.transaction').click(function() {
        $(this).find('.posting').toggleClass("hidden");
    });

    // Toggle entries with checkboxes
    $('#entry-filters input').click(function() {
        event.preventDefault();
        var $this = $(this);
        var selector = $this.attr('data-selector');
        var shouldShow = $this.hasClass('inactive');

        if ($this.val() == 'Transaction') {
            $('#entry-filters .txn-toggle').toggleClass('inactive', !shouldShow);
        }

        $('#journal-table ' + selector).toggleClass('hidden', !shouldShow);
        $this.toggleClass('inactive', !shouldShow);

        // Modify get params
        const queryHash = queryString.parse(location.search);
        var type = $this.attr('data-type');
        var defaultShow = $this.attr('data-show-default') === 'true';

        if (shouldShow !== defaultShow) {
            queryHash[type] = shouldShow;
        } else if (type in queryHash) {
            delete queryHash[type];
        }

        window.history.pushState('', '', '?' + queryString.stringify(queryHash));
    });
}
