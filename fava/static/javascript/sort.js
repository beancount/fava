/* global tinysort */
import 'tinysort';
import { $, $$ } from './helpers';

// Enable sorting of tables and the journal.
//
// Only clicking on headers that have a data-sort attribute will have an
// effect. Usually tinysort is smart enough to correctly sort the lists.  For
// dates, set data-sort="date" and if data-sort-value on the individual items
// should be used for sorting, set data-sort="data".

function getSortOrder(headerElement) {
  if (!headerElement.getAttribute('data-order')) {
    return headerElement.getAttribute('data-sort-default') || 'asc';
  }
  return headerElement.getAttribute('data-order') === 'asc' ? 'desc' : 'asc';
}

function sortableJournal(ol) {
  const head = $('.head', ol);
  const headers = $$('span[data-sort]', head);

  head.addEventListener('click', (event) => {
    const header = event.target.closest('span');
    if (!header.getAttribute('data-sort')) {
      return;
    }
    const order = getSortOrder(header);
    const headerClass = header.classList[0];

    // update sort order
    headers.forEach((el) => { el.removeAttribute('data-order'); });
    header.setAttribute('data-order', order);

    tinysort([].slice.call(ol.children, 1), {
      selector: `span.${headerClass}`,
      order,
      ignoreDashes: header.getAttribute('data-sort') === 'date',
    });
  });
}

function sortableTable(table) {
  const head = $('thead', table);
  const headers = $$('th[data-sort]', head);

  head.addEventListener('click', (event) => {
    const header = event.target.closest('th');
    if (!header.getAttribute('data-sort')) {
      return;
    }
    const order = getSortOrder(header);

    // update sort order
    headers.forEach((el) => { el.removeAttribute('data-order'); });
    header.setAttribute('data-order', order);

    tinysort(table.querySelector('tbody').querySelectorAll('tr'), {
      selector: `td:nth-child(${headers.indexOf(header) + 1})`,
      order,
      data: header.getAttribute('data-sort') === 'data' ? 'sort-value' : null,
      ignoreDashes: header.getAttribute('data-sort') === 'date',
    });
  });
}

export default function initSort() {
  $$('.sortable').forEach((el) => {
    sortableTable(el);
  });
  $$('ol.journal-table').forEach((el) => {
    sortableJournal(el);
  });
}
