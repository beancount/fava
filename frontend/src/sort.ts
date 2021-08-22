/**
 * Sorting of tables and the journal.
 *
 * Only clicking on headers that have a data-sort attribute will have an
 * effect. The currently supported values for `data-sort` are:
 *
 *  - 'string': Case-insensitive string comparison.
 *  - 'num': Clean and parse to float.
 */

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
function getValue(el: HTMLElement | null): string {
  return el?.getAttribute("data-sort-value") || el?.textContent || "";
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
 * @param parent - The element that the sorted children should be inserted into.
 * @param elements - The elements to sort (children of parent).
 * @param selector - Selector for the column that should be sorted by.
 * @param order - The sort order.
 * @param type - The type of the value that should be sorted by.
 */
function sortElements<T extends Element, C extends HTMLElement>(
  parent: Element,
  elements: T[],
  selector: (e: T) => C | null,
  order: SortOrder,
  type: string | null
): void {
  const sortFunction = sortFunc(type, order, (a: T) => getValue(selector(a)));
  const fragment = document.createDocumentFragment();
  elements.sort(sortFunction).forEach((el) => {
    fragment.appendChild(el);
  });
  parent.appendChild(fragment);
}

/**
 * Obtain the sort order for the row from the row header
 * @param headerElement - The element to get the sort order from.
 */
function getSortOrder(headerElement: Element): SortOrder {
  if (!headerElement.getAttribute("data-order")) {
    return headerElement.getAttribute("data-sort-default") === "desc"
      ? "desc"
      : "asc";
  }
  return headerElement.getAttribute("data-order") === "asc" ? "desc" : "asc";
}

/**
 * Make the Fava journal sortable.
 * @param ol - the <ol> element.
 */
export function sortableJournal(ol: HTMLOListElement): void {
  const head = ol.querySelector(".head");
  if (!head) {
    return;
  }
  const headers = head.querySelectorAll("span[data-sort]");

  headers.forEach((header) => {
    header.addEventListener("click", () => {
      const order = getSortOrder(header);
      const type = header.getAttribute("data-sort");
      const headerClass = header.classList[0];

      // update sort order
      headers.forEach((el) => {
        el.removeAttribute("data-order");
      });
      header.setAttribute("data-order", order);

      sortElements(
        ol,
        [].slice.call(ol.children, 1),
        (li: HTMLLIElement): HTMLElement | null =>
          li.querySelector(`.${headerClass}`),
        order,
        type
      );
    });
  });
}

export class SortableTable extends HTMLTableElement {
  constructor() {
    super();

    const body = this.tBodies.item(0);
    if (!this.tHead || !body) {
      return;
    }
    const headers = [...this.tHead.querySelectorAll("th[data-sort]")];

    headers.forEach((header) => {
      header.addEventListener("click", () => {
        const order = getSortOrder(header);
        const type = header.getAttribute("data-sort");
        const index = headers.indexOf(header);

        // update sort order
        headers.forEach((el) => {
          el.removeAttribute("data-order");
        });
        header.setAttribute("data-order", order);

        sortElements(
          body,
          [...body.querySelectorAll("tr")],
          (tr: HTMLTableRowElement): HTMLElement | null => tr.cells.item(index),
          order,
          type
        );
      });
    });
  }
}
