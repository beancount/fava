const tinysort = require('tinysort');

export default function makeSortable(table) {
  const tableHead = table.querySelector('thead');
  const tableHeaders = tableHead.querySelectorAll('th');

  tableHead.addEventListener('click', (event) => {
    let tableHeader = event.target;

    while (tableHeader.nodeName !== 'TH') {
      tableHeader = tableHeader.parentNode;
    }

    const index = Array.prototype.indexOf.call(tableHeaders, tableHeader);

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
      selector: `td:nth-child(${index + 1})`,
      order,
    });
  });
}
