/**
 * Sorting of tables and the journal.
 *
 * Only clicking on headers that have a data-sort attribute will have an
 * effect. The currently supported values for `data-sort` are:
 *
 *  - 'string': Case-insensitive string comparison.
 *  - 'num': Clean and parse to float.
 */

import { select, selectAll } from "./helpers";
import e from "./events";

function parseNumber(num: string): number {
  const cleaned = num.replace(/[^\-?0-9.]/g, "");
  const n = parseFloat(cleaned);
  return Number.isNaN(n) ? 0 : n;
}

function stringComparator(A: string, B: string): number {
  const a = A.toLowerCase();
  const b = B.toLowerCase();

  if (a === b) {
    return 0;
  }
  return a < b ? -1 : 1;
}
function numComparator(a: string, b: string): number {
  return parseNumber(a) - parseNumber(b);
}

type SortOrder = "desc" | "asc";

/**
 * Obtain the value to sort by for an element.
 */
function getValue(el: HTMLElement): string {
  return el.getAttribute("data-sort-value") || el.textContent || el.innerText;
}

/**
 * Generate a sort function for a given comparison type, using a getter
 */
export function sortFunc<T>(
  type: string | null,
  order: SortOrder,
  getter: (e: T) => string
): (a: T, b: T) => number {
  const comparator = type === "num" ? numComparator : stringComparator;
  function func(a: T, b: T): number {
    return (order === "asc" ? 1 : -1) * comparator(getter(a), getter(b));
  }
  return func;
}

/**
 * Sort elements contained in a given parent element.
 */
function sortElements<T extends Element, C extends HTMLElement>(
  parent: Element,
  elements: T[],
  selector: (e: T) => C,
  order: SortOrder,
  type: string | null
): void {
  const sortFunction = sortFunc(type, order, (a: T) => getValue(selector(a)));
  const fragment = document.createDocumentFragment();
  elements.sort(sortFunction).forEach(el => {
    fragment.appendChild(el);
  });
  parent.appendChild(fragment);
}

/**
 * Obtain the sort order for the row from the row header
 */
function getSortOrder(headerElement: Element): SortOrder {
  if (!headerElement.getAttribute("data-order")) {
    return headerElement.getAttribute("data-sort-default") === "desc"
      ? "desc"
      : "asc";
  }
  return headerElement.getAttribute("data-order") === "asc" ? "desc" : "asc";
}

function sortableJournal(ol: HTMLOListElement): void {
  const head = select(".head", ol);
  if (!head) {
    return;
  }
  const headers = selectAll("span[data-sort]", head);

  headers.forEach(header => {
    header.addEventListener("click", () => {
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
  });
}

function sortableTable(table: HTMLTableElement): void {
  const head = table.tHead;
  const body = table.tBodies.item(0);
  if (!head || !body) {
    return;
  }
  const headers = selectAll("th[data-sort]", head);

  headers.forEach(header => {
    header.addEventListener("click", () => {
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
          // eslint-disable-next-line
          return tr.cells.item(index)!;
        },
        order,
        type
      );
    });
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
