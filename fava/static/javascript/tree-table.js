export default function initTreeTable() {
  $('.tree-table').on('click', 'span.has-children', (event) => {
    const row = $(event.currentTarget).parents('li').first();
    if (event.shiftKey) {
      row.find('li').toggleClass('toggled', !row.hasClass('toggled'));
    }
    if (event.ctrlKey || event.metaKey) {
      row.find('li').toggleClass('toggled', row.hasClass('toggled'));
    }
    row.toggleClass('toggled');
    row.parents('ol').find('a.expand-all')
      .toggleClass('hidden', row.parents('ol').find('li.toggled'));
  });

  $('.tree-table').on('click', 'a.expand-all', (event) => {
    event.preventDefault();
    const $this = $(event.target);
    $this.parents('ol').find('li.toggled').removeClass('toggled');
    $this.addClass('hidden');
  });
}
