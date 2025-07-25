import { localStorageSyncedStore } from "../lib/store";
import { array, constants, tuple, type ValidationT } from "../lib/validation";

const journalShowEntryValidator = constants(
  "open",
  "close",
  "transaction",
  "cleared",
  "pending",
  "other",
  "balance",
  "note",
  "document",
  "discovered",
  "linked",
  "pad",
  "query",
  "statement",
  "custom",
  "budget",
  "metadata",
  "postings",
  null,
)

export type JournalShowEntry = ValidationT<typeof journalShowEntryValidator>

const defaultValue: JournalShowEntry[] = [
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
  array(journalShowEntryValidator),
  () => defaultValue,
);

const sortOrderValidator = tuple(constants("date", "flag", "narration", null), constants("asc", "desc", null));
export type JournalSortOrder = ValidationT<typeof sortOrderValidator>

const defaultSortOrder: JournalSortOrder = ["date", "desc"];

/** The column and order that the journal should be sorted in. */
export const journalSortOrder = localStorageSyncedStore(
  "journal-sort-order",
  sortOrderValidator,
  () => defaultSortOrder,
);
