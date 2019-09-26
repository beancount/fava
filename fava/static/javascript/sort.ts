// Sorting of tables and the journal.
//
// Only clicking on headers that have a data-sort attribute will have an
// effect. The currently supported values for `data-sort` are:
//
//  - 'string': Case-insensitive string comparison.
//  - 'num': Clean and parse to float.

import { select, selectAll } from "./helpers";
import e from "./events";

function parseNumber(num: string): number {
  const cleaned = num.replace(/[^\-?0-9.]/g, "");
  const n = parseFloat(cleaned);
  return Number.isNaN(n) ? 0 : n;
}

function stringSorter(A: string, B: string) {
  const a = A.toLowerCase();
  const b = B.toLowerCase();

  if (a === b) return 0;
  if (a < b) return -1;
  return 1;
}
function numSorter(a: string, b: string) {
  return parseNumber(a) - parseNumber(b);
}

type SortOrder = "desc" | "asc";

function getValue(el: HTMLElement) {
  return el.getAttribute("data-sort-value") || el.textContent || el.innerText;
}

function sortElements<T extends Element, C extends HTMLElement>(
  parent: Element,
  elements: T[],
  selector: (e: T) => C,
  order: SortOrder,
  type: string | null
) {
  const sorter = type === "num" ? numSorter : stringSorter;
  function sortFunction(a: T, b: T) {
    return (
      (order === "asc" ? 1 : -1) *
      sorter(getValue(selector(a)), getValue(selector(b)))
    );
  }

  const fragment = document.createDocumentFragment();
  elements.sort(sortFunction).forEach(el => {
    fragment.appendChild(el);
  });
  parent.appendChild(fragment);
}

function getSortOrder(headerElement: Element): SortOrder {
  if (!headerElement.getAttribute("data-order")) {
    return headerElement.getAttribute("data-sort-default") === "desc"
      ? "desc"
      : "asc";
  }
  return headerElement.getAttribute("data-order") === "asc" ? "desc" : "asc";
}

function sortableJournal(ol: HTMLOListElement) {
  const head = select(".head", ol);
  if (!head) return;
  const headers = selectAll("span[data-sort]", head);

  head.addEventListener("click", event => {
    const header = (event.target as HTMLElement).closest("span");
    if (!header || !header.getAttribute("data-sort")) {
      return;
    }
    const order = getSortOrder(header);
    const type = header.getAttribute("data-sort");
    const headerClass = header.classList[0];

    // update sort order
    headers.forEach(el => {
      el.removeAttribute("data-order");
    });
    header.setAttribute("data-order", order);

    sortElements(
      ol,
      [].slice.call(ol.children, 1),
      function selector(li: HTMLLIElement): HTMLElement {
        return li.querySelector(`.${headerClass}`) as HTMLElement;
      },
      order,
      type
    );
  });
}

function sortableTable(table: HTMLTableElement) {
  const head = table.tHead;
  const body = table.tBodies.item(0);
  if (!head || !body) return;
  const headers = selectAll("th[data-sort]", head);

  head.addEventListener("click", event => {
    const header = (event.target as HTMLElement).closest("th");
    if (!header || !header.getAttribute("data-sort")) {
      return;
    }
    const order = getSortOrder(header);
    const type = header.getAttribute("data-sort");
    const index = headers.indexOf(header);

    // update sort order
    headers.forEach(el => {
      el.removeAttribute("data-order");
    });
    header.setAttribute("data-order", order);

    sortElements(
      body,
      selectAll("tr", body) as HTMLTableRowElement[],
      function selector(tr: HTMLTableRowElement): HTMLTableDataCellElement {
        return tr.cells.item(index)!;
      },
      order,
      type
    );
  });
}

export default function initSort() {
  selectAll("table.sortable").forEach(el => {
    sortableTable(el as HTMLTableElement);
  });
  selectAll("ol.journal").forEach(el => {
    sortableJournal(el as HTMLOListElement);
  });
}

e.on("page-loaded", () => {
  initSort();
});
