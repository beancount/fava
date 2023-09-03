import { localStorageSyncedStore } from "../lib/store";
import { array, constant, string, tuple, union } from "../lib/validation";

const defaultValue = [
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
export const journalShow = localStorageSyncedStore(
  "journal-show",
  array(string),
  () => defaultValue,
);

const defaultSortOrder: [string, "asc" | "desc"] = ["date", "desc"];

/** The column and order that the journal should be sorted in. */
export const journalSortOrder = localStorageSyncedStore(
  "journal-sort-order",
  tuple([string, union(constant("asc"), constant("desc"))]),
  () => defaultSortOrder,
);
