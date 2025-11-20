import { localStorageSyncedStore } from "../lib/store.ts";
import { array, constants, string, tuple } from "../lib/validation.ts";
import type { JournalSortColumn } from "../reports/journal/sort.ts";

const default_journal_show = [
  "balance",
  "budget",
  "cleared",
  "custom",
  "discovered",
  "document",
  "note",
  "pending",
  "query",
  "statement",
  "transaction",
];

/** The types of entries to show in the journal. */
export const journal_show = localStorageSyncedStore(
  "journal-show",
  array(string),
  () => default_journal_show,
);

export type JournalSort = [JournalSortColumn, "asc" | "desc"];
const default_journal_sort: JournalSort = ["date", "desc"];

/** The column and order that the journal should be sorted in. */
export const journal_sort = localStorageSyncedStore<JournalSort>(
  "journal-sort-order",
  tuple(constants("date", "flag", "narration"), constants("asc", "desc")),
  () => default_journal_sort,
);
