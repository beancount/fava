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

export type SortOrder = "asc" | "desc";
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
  readonly column: SortColumn<T>;
  readonly order: SortOrder;

  constructor(column: SortColumn<T>, order: SortOrder) {
    this.column = column;
    this.order = order;
  }

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
 * Sort array with provided string value getter.
 */
export function sort_by_strings<T>(
  data: readonly T[],
  value: (v: T) => string,
): T[] {
  return sort_internal(data, value, compare_strings, 1);
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
): T[] {
  const indices = Uint32Array.from(data, (_d, i) => i);
  const values = data.map(value);
  // values and indices are of the same length (as data), so this is safe
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  indices.sort((a, b) => direction * compare(values[a]!, values[b]!));
  return permute(data, indices);
}

/** A SortColumn that does no sorting. */
export class UnsortedColumn<T> implements SortColumn<T> {
  readonly name: string;
  constructor(name: string) {
    this.name = name;
  }

  sort(data: readonly T[]): readonly T[] {
    return data;
  }
}

/** A SortColumn for numbers. */
export class NumberColumn<T> implements SortColumn<T> {
  private compare = (a: number, b: number): number => a - b;
  readonly name: string;
  private readonly value: (row: Readonly<T>) => number;

  constructor(name: string, value: (row: Readonly<T>) => number) {
    this.name = name;
    this.value = value;
  }

  sort(data: readonly T[], direction: SortDirection): readonly T[] {
    return sort_internal(data, this.value, this.compare, direction);
  }
}
/** A SortColumn for objects with a string date property. */
export class DateColumn<T extends { date: string }> extends NumberColumn<T> {
  constructor(name: string) {
    super(name, (d: T) => new Date(d.date).valueOf());
  }
}
/** A SortColumn for strings. */
export class StringColumn<T> implements SortColumn<T> {
  private compare = compare_strings;
  readonly name: string;
  private readonly value: (row: Readonly<T>) => string;

  constructor(name: string, value: (row: Readonly<T>) => string) {
    this.name = name;
    this.value = value;
  }

  sort(data: readonly T[], direction: 1 | -1): readonly T[] {
    return sort_internal(data, this.value, this.compare, direction);
  }
}

/** Parse a number from the string, ignoring all other characters. */
function parse_number(num: string): number {
  const cleaned = num.replace(/[^\-?0-9.]/g, "");
  const n = Number.parseFloat(cleaned);
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
