const URI = require('urijs');

module.exports.initJournal = function initJournal() {
  // Toggle legs by clicking on transaction/padding row
  $('#journal-table li.transaction').click((event) => {
    $(event.currentTarget).find('.posting').toggleClass('hidden');
  });

  // Toggle entries with checkboxes
  $('#entry-filters input').click((event) => {
    event.preventDefault();
    const $this = $(event.currentTarget);
    const selector = $this.attr('data-selector');
    const shouldShow = $this.hasClass('inactive');

    if ($this.val() === 'Transaction') {
      $('#entry-filters .txn-toggle').toggleClass('inactive', !shouldShow);
    }

    $(`#journal-table ${selector}`).toggleClass('hidden', !shouldShow);
    $this.toggleClass('inactive', !shouldShow);

    // Modify get params
    const filterShow = [];
    $('#entry-filters input').each((_, el) => {
      const $el = $(el);
      if (!$el.hasClass('inactive')) {
        filterShow.push($el.attr('data-type'));
      }
    });

    const url = new URI(window.location)
      .setSearch({ show: filterShow });
    window.history.pushState('', '', url.toString());
    return false;
  });
};
