// Account trees.
//
// This handles the toggling of accounts in the accounts trees.

import { $, $$ } from './helpers';
import e from './events';

e.on('page-loaded', () => {
  $$('.tree-table').forEach((table) => {
    $.delegate(table, 'click', 'span.has-children', (event) => {
      if (event.target.tagName === 'A') {
        return;
      }
      const row = event.target.closest('li');
      const willShow = row.classList.contains('toggled');
      if (event.shiftKey) {
        $$('li', row).forEach((el) => { el.classList.toggle('toggled', !willShow); });
      }
      if (event.ctrlKey || event.metaKey) {
        $$('li', row).forEach((el) => { el.classList.toggle('toggled', willShow); });
      }
      row.classList.toggle('toggled');

      $('.expand-all', table)
        .classList.toggle('hidden', !$$('.toggled', table).length);
    });

    $.delegate(table, 'click', '.expand-all', (event) => {
      event.target.classList.add('hidden');
      $$('.toggled', table).forEach((el) => { el.classList.remove('toggled'); });
    });
  });
});
