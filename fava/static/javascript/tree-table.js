import { $, $$ } from './helpers';

export default function initTreeTable() {
  $$('.tree-table').forEach((table) => {
    $.delegate(table, 'click', 'span.has-children', (event) => {
      const row = event.target.closest('li');
      const willShow = row.classList.contains('toggled');
      if (event.shiftKey) {
        $$('li', row).forEach((el) => { el.classList.toggle('toggled', !willShow); });
      }
      if (event.ctrlKey || event.metaKey) {
        $$('li', row).forEach((el) => { el.classList.toggle('toggled', willShow); });
      }
      row.classList.toggle('toggled');

      $('a.expand-all', table)
        .classList.toggle('hidden', !$$('.toggled', table).length);
    });

    $.delegate(table, 'click', 'a.expand-all', (event) => {
      event.preventDefault();
      event.target.classList.add('hidden');
      $$('.toggled', table).forEach((el) => { el.classList.remove('toggled'); });
    });
  });
}
