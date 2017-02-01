import URI from 'urijs';

import { $, $$ } from './helpers';

export default function initJournal() {
  const journal = $('#journal-table');
  if (!journal) return;

  // Toggle postings by clicking on transaction row.
  $.delegate(journal, 'click', '.transaction', (event) => {
    $('.postings', event.target.closest('.transaction')).classList.toggle('hidden');
    if ($('.metadata', event.target.closest('.transaction'))) {
      $('.metadata', event.target.closest('.transaction')).classList.toggle('hidden');
    }
  });

  // Toggle entries with buttons.
  $$('#entry-filters button').forEach((button) => {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      const type = button.getAttribute('data-type');
      const shouldShow = button.classList.contains('inactive');

      button.classList.toggle('inactive', !shouldShow);
      if (type === 'transaction') {
        $$('#entry-filters .txn-toggle').forEach((el) => { el.classList.toggle('inactive', !shouldShow); });
      }

      if (type === 'custom') {
        $$('#entry-filters .custom-toggle').forEach((el) => { el.classList.toggle('inactive', !shouldShow); });
      }

      if (type === 'document') {
        $$('#entry-filters .doc-toggle').forEach((el) => { el.classList.toggle('inactive', !shouldShow); });
      }

      $$(`#journal-table .${type}`).forEach((el) => { el.classList.toggle('hidden', !shouldShow); });

      // Modify get params
      const filterShow = [];
      $$('#entry-filters button').forEach((el) => {
        if (!el.classList.contains('inactive')) {
          filterShow.push(el.getAttribute('data-type'));
        }
      });

      const url = new URI(window.location)
        .setSearch({ show: filterShow });
      window.history.pushState(null, null, url.toString());
    });
  });
}
