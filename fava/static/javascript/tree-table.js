export default function initTreeTable() {
  $('.tree-table').on('click', 'span.has-children', (event) => {
    const row = event.currentTarget.parentNode.parentNode;
    const $row = $(row);
    if (event.shiftKey) {
      $row.find('li').toggleClass('toggled', !row.classList.contains('toggled'));
    }
    if (event.ctrlKey || event.metaKey) {
      $row.find('li').toggleClass('toggled', row.classList.contains('toggled'));
    }
    row.classList.toggle('toggled');
    $row.parents('ol').find('a.expand-all')
      .toggleClass('hidden', $row.parents('ol').find('li.toggled'));
  });

  $('.tree-table').on('click', 'a.expand-all', (event) => {
    event.preventDefault();
    event.target.classList.add('hidden');
    $(event.target).parents('ol').find('li.toggled').removeClass('toggled');
  });
}
