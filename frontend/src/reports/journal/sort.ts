import { get_direction, sortElements } from "../../sort/index.ts";
import type { JournalSort } from "../../stores/journal.ts";

export type JournalSortColumn = "date" | "flag" | "narration";

const journal_column_types = {
  date: "num",
  flag: "string",
  narration: "string",
};

const journal_column_selectors = {
  date: ".datecell",
  flag: ".flag",
  narration: ".description",
};

export function sort_journal(ol: HTMLOListElement, sort: JournalSort): void {
  const [column, order] = sort;
  const type = journal_column_types[column];
  const selector = journal_column_selectors[column];
  sortElements<HTMLLIElement>(
    ol,
    [].slice.call(ol.children),
    (li) => li.querySelector(selector),
    get_direction(order),
    type,
  );
}
