import { $, $$ } from './helpers';

// Enable sorting of tables and the journal.
//
// Only clicking on headers that have a data-sort attribute will have an
// effect. The currently supported values for `data-sort` are:
//
//  - 'string': Case-insensitive string comparison.
//  - 'num': Clean and parse to float.
//

function parseNumber(num) {
  const cleaned = num.replace(/[^\-?0-9.]/g, '');
  const n = parseFloat(cleaned);
  return isNaN(n) ? 0 : n;
}

const sorters = {
  string(A, B) {
    const a = A.toLowerCase();
    const b = B.toLowerCase();

    if (a === b) return 0;
    if (a < b) return -1;
    return 1;
  },
  num(a, b) {
    return parseNumber(a) - parseNumber(b);
  },
};

function getValue(el) {
  return el.getAttribute('data-sort-value') || el.textContent || el.innerText;
}

function sortElements(options) {
  function sortFunction(a, b) {
    return (options.order === 'asc' ? 1 : -1) * sorters[options.type](
        getValue(options.selector(a)),
        getValue(options.selector(b)));
  }

  const fragment = document.createDocumentFragment();
  options.elements.sort(sortFunction).forEach((el) => {
    fragment.appendChild(el);
  });
  options.parent.appendChild(fragment);
}

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
    const type = header.getAttribute('data-sort');
    const headerClass = header.classList[0];

    // update sort order
    headers.forEach((el) => { el.removeAttribute('data-order'); });
    header.setAttribute('data-order', order);

    sortElements({
      parent: ol,
      elements: [].slice.call(ol.children, 1),
      selector(li) {
        return li.querySelector(`.${headerClass}`);
      },
      order,
      type,
    });
  });
}

function sortableTable(table) {
  const head = table.tHead;
  const headers = $$('th[data-sort]', head);

  head.addEventListener('click', (event) => {
    const header = event.target.closest('th');
    if (!header.getAttribute('data-sort')) {
      return;
    }
    const order = getSortOrder(header);
    const type = header.getAttribute('data-sort');
    const index = headers.indexOf(header);

    // update sort order
    headers.forEach((el) => { el.removeAttribute('data-order'); });
    header.setAttribute('data-order', order);

    sortElements({
      parent: table.querySelector('tbody'),
      elements: $$('tr', table.querySelector('tbody')),
      selector(tr) {
        return tr.cells.item(index);
      },
      order,
      type,
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
