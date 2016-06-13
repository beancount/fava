const URI = require('urijs');

module.exports.initJournal = function initJournal() {
  // Toggle legs by clicking on transaction/padding row
  $('#journal-table li.transaction').click((event) => {
    $(event.currentTarget).find('.posting').toggleClass('hidden');
  });

  // Toggle entries with checkboxes
  $('#entry-filters input').click(function() {
    event.preventDefault();
    const $this = $(this);
    const selector = $this.attr('data-selector');
    const shouldShow = $this.hasClass('inactive');

    if ($this.val() === 'Transaction') {
      $('#entry-filters .txn-toggle').toggleClass('inactive', !shouldShow);
    }

    $('#journal-table ' + selector).toggleClass('hidden', !shouldShow);
    $this.toggleClass('inactive', !shouldShow);

    // Modify get params
    const url = new URI(window.location);
    let modified = false;
    const filterShow = [];
    $('#entry-filters input').each(function() {
      const $this = $(this);
      const shouldShow = $this.hasClass('inactive');
      const defaultShow = $this.attr('data-show-default') === 'true';
      if (shouldShow === defaultShow) {
        modified = true;
      }
      if (!shouldShow) {
        filterShow.push($this.attr('data-type'));
      }
    });

    if (modified) {
      url.setSearch({
        show: filterShow,
      });
    } else {
      url.removeSearch(['show']);
    }

    window.history.pushState('', '', url.toString());
    return false;
  });
};
