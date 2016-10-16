const URI = require('urijs');

export default function initJournal() {
  // Toggle postings by clicking on transaction row.
  $('#journal-table').on('click', '.transaction', (event) => {
    $(event.currentTarget).find('.postings').toggleClass('hidden');
  });

  // Toggle entries with buttons.
  $('#entry-filters button').click((event) => {
    event.preventDefault();
    const $this = $(event.currentTarget);
    const type = $this.data('type');
    const shouldShow = $this.hasClass('inactive');

    if (type === 'transaction') {
      $('#entry-filters .txn-toggle').toggleClass('inactive', !shouldShow);
    }

    $(`#journal-table .${type}`).toggleClass('hidden', !shouldShow);
    $this.toggleClass('inactive', !shouldShow);

    // Modify get params
    const filterShow = [];
    $('#entry-filters button').each((_, el) => {
      const $el = $(el);
      if (!$el.hasClass('inactive')) {
        filterShow.push($el.data('type'));
      }
    });

    const url = new URI(window.location)
      .setSearch({ show: filterShow });
    window.history.pushState('', '', url.toString());
  });
}
