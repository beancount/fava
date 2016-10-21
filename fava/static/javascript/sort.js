import { $, $$ } from './helpers';

const tinysort = require('tinysort');

function makeSortable(table) {
  const tableHead = $('thead', table);
  const tableHeaders = $$('th', tableHead);

  tableHead.addEventListener('click', (event) => {
    let tableHeader = event.target;

    while (tableHeader.nodeName !== 'TH') {
      tableHeader = tableHeader.parentNode;
    }

    let order;
    if (!tableHeader.getAttribute('data-order')) {
      order = tableHeader.getAttribute('data-sort-default') || 'asc';
    } else {
      order = tableHeader.getAttribute('data-order') === 'asc' ? 'desc' : 'asc';
    }

    // update sort order
    tableHeaders.forEach((el) => { el.removeAttribute('data-order'); });
    tableHeader.setAttribute('data-order', order);

    tinysort(table.querySelector('tbody').querySelectorAll('tr'), {
      selector: `td:nth-child(${tableHeaders.indexOf(tableHeader) + 1})`,
      order,
    });
  });
}

export default function initSort() {
  $$('table.sortable').forEach((el) => {
    makeSortable(el);
  });
}
