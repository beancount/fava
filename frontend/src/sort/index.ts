/**
 * Sorting of tables and the journal.
 *
 * Only clicking on headers that have a data-sort attribute will have an
 * effect. The currently supported values for `data-sort` are:
 *
 *  - 'string': Case-insensitive string comparison.
 *  - 'num': Clean and parse to float.
 *
 * For the tables that are rendered in Svelte components, the logic necessary
 * for sorting is also provided here (SortColumn and Sorter)
 */

import { permute } from "d3-array";
import { get as store_get } from "svelte/store";

import { journalSortOrder } from "../stores/journal";

type SortOrder = "asc" | "desc";
type SortDirection = 1 | -1;

export const get_direction = (o: SortOrder): SortDirection =>
  o === "asc" ? 1 : -1;

const collator = Intl.Collator();
/** A compare function for strings using the default browser locale. */
const compare_strings = collator.compare.bind(collator);

/**
 * A column that can be used for sorting in some data.
 *
 * The data is simply an array of values, and this specifies a getter to be used
 * to sort by this column. On sorting, this getter will be invoked once per element.
 */
export interface SortColumn<T = unknown> {
  /** The name of this column, usually to be used as a header in the table. */
  readonly name: string;

  /** Sort the data in the given direction. */
  sort(data: readonly T[], direction: SortDirection): readonly T[];
}

/** A sorter of tabular data, is specified by a SortColumn and an order to sort by. */
export class Sorter<T = unknown> {
  constructor(
    readonly column: SortColumn<T>,
    readonly order: SortOrder,
  ) {}

  /** Get a new sorter by switching to a possibly different column. */
  switchColumn(column: SortColumn<T>): Sorter<T> {
    if (column === this.column) {
      return new Sorter(column, this.order === "asc" ? "desc" : "asc");
    }
    return new Sorter(column, "asc");
  }

  /** Sort the data. */
  sort(data: readonly T[]): readonly T[] {
    return this.column.sort(data, get_direction(this.order));
  }
}

/**
 * Sort array with provided value getter and compare function.
 * Calls the value getter only once per element.
 */
function sort_internal<T, U>(
  data: readonly T[],
  value: (row: T) => U,
  compare: (a: U, b: U) => number,
  direction: SortDirection,
) {
  const indices = Uint32Array.from(data, (_d, i) => i);
  const values = data.map(value);
  // values and indices are of the same length (as data), so this is safe
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  indices.sort((a, b) => direction * compare(values[a]!, values[b]!));
  return permute(data, indices);
}

/** A SortColumn that does no sorting. */
export class UnsortedColumn<T> implements SortColumn<T> {
  constructor(readonly name: string) {}

  sort(data: readonly T[]): readonly T[] {
    return data;
  }
}

/** A SortColumn for numbers. */
export class NumberColumn<T> implements SortColumn<T> {
  private compare = (a: number, b: number): number => a - b;

  constructor(
    readonly name: string,
    private readonly value: (row: Readonly<T>) => number,
  ) {}

  sort(data: readonly T[], direction: SortDirection): readonly T[] {
    return sort_internal(data, this.value, this.compare, direction);
  }
}
/** A SortColumn for objects with a string date property. */
export class DateColumn<T extends { date: string }> extends NumberColumn<T> {
  constructor(readonly name: string) {
    super(name, (d: T) => new Date(d.date).valueOf());
  }
}
/** A SortColumn for strings. */
export class StringColumn<T> implements SortColumn<T> {
  private compare: (x: string, y: string) => number = compare_strings;

  constructor(
    readonly name: string,
    private readonly value: (row: Readonly<T>) => string,
  ) {}

  sort(data: readonly T[], direction: 1 | -1): readonly T[] {
    return sort_internal(data, this.value, this.compare, direction);
  }
}

/** Parse a number from the string, ignoring all other characters. */
function parse_number(num: string): number {
  const cleaned = num.replace(/[^\-?0-9.]/g, "");
  const n = parseFloat(cleaned);
  return Number.isNaN(n) ? 0 : n;
}

/** A function to compare strings which should contain numbers. */
function compare_numbers(a: string, b: string): number {
  return parse_number(a) - parse_number(b);
}

/**
 * Sort elements contained in a given parent element.
 * @param parent - The element that the sorted children should be inserted into.
 * @param elements - The elements to sort (children of parent).
 * @param selector - Selector for the column that should be sorted by.
 * @param order - The sort order.
 * @param type - The type of the value that should be sorted by.
 */
export function sortElements<T extends Element>(
  parent: Element,
  elements: T[],
  selector: (e: T) => Element | null,
  direction: SortDirection,
  type: string | null,
): void {
  const comparator = type === "num" ? compare_numbers : compare_strings;
  const value = (a: T) => {
    const el = selector(a);
    return el?.getAttribute("data-sort-value") ?? el?.textContent ?? "";
  };
  const sorted_elements = sort_internal(elements, value, comparator, direction);
  const fragment = document.createDocumentFragment();
  sorted_elements.forEach((el) => {
    fragment.appendChild(el);
  });
  parent.appendChild(fragment);
}

/**
 * Make the Fava journal sortable.
 * @param ol - the <ol> element.
 */
export function sortableJournal(ol: HTMLOListElement): void {
  const head = ol.querySelector(".head");
  if (!head) {
    throw new Error("Journal is missing header.");
  }
  const headers = head.querySelectorAll("span[data-sort]");
  const [initialColumn, initialOrder] = store_get(journalSortOrder);
  headers.forEach((header) => {
    const headerClass = header.classList[0];
    const name = header.getAttribute("data-sort-name");
    const type = header.getAttribute("data-sort");
    if (headerClass == null || name == null || type == null) {
      throw new Error(`Journal has invalid header: ${header.innerHTML}.`);
    }

    const sort = (order: SortOrder) => {
      // update displayed sort order
      headers.forEach((el) => {
        el.removeAttribute("data-order");
      });
      header.setAttribute("data-order", order);
      // sort elements
      sortElements<HTMLLIElement>(
        ol,
        [].slice.call(ol.children, 1),
        (li) => li.querySelector(`.${headerClass}`),
        get_direction(order),
        type,
      );
    };
    if (name === initialColumn) {
      sort(initialOrder);
    }

    header.addEventListener("click", () => {
      const order =
        header.getAttribute("data-order") === "asc" ? "desc" : "asc";
      sort(order);
      journalSortOrder.set([name, order]);
    });
  });
}
