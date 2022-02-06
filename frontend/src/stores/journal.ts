import { localStorageSyncedStore } from "../lib/store";
import { array, string } from "../lib/validation";

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
  () => defaultValue
);
