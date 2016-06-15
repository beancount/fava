module.exports.initTreeTable = function initTreeTable() {
  $('ol.tree-table span.has-children').click((event) => {
    const row = $(event.currentTarget).parents('li').first();
    if (event.shiftKey === true) {
      row.find('li').toggleClass('toggled', !row.hasClass('toggled'));
    }
    row.toggleClass('toggled');
    row.parents('ol').find('a.expand-all')
      .toggleClass('hidden', row.parents('ol').find('li.toggled'));
  });

  $('ol.tree-table').on('click', 'a.expand-all', (event) => {
    event.preventDefault();
    const $this = $(event.target);
    $this.parents('ol').find('li.toggled').removeClass('toggled');
    $this.addClass('hidden');
  });
};
