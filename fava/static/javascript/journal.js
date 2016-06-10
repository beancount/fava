const URI = require('urijs');

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
        var url = URI(window.location);
        var modified = false;
        var filterShow = [];
        $('#entry-filters input').each(function() {
            var $this = $(this);
            var shouldShow = $this.hasClass('inactive');
            var defaultShow = $this.attr('data-show-default') === 'true';
            if (shouldShow === defaultShow) {
                modified = true;
            }
            if (!shouldShow) {
                filterShow.push($this.attr('data-type'));
            }
        });

        if (modified) {
            url.setSearch({ show : filterShow });
        } else {
            url.removeSearch(['show']);
        }

        window.history.pushState('', '', url.toString());
        return false;
    });
}
