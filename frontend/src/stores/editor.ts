import { writable } from "svelte/store";

import type { Balance, Note, Transaction } from "../entries/index.ts";
import { localStorageSyncedStore } from "../lib/store.ts";
import { boolean } from "../lib/validation.ts";

/** Whether to reload after saving an entry in the slice editor. */
export const reloadAfterSavingEntrySlice = localStorageSyncedStore(
  "reload-after-saving-entry-slice",
  boolean,
  () => true,
);

/** Whether to continue (and add another entry) after adding an entry in the AddEntry dialog. */
export const addEntryContinue = localStorageSyncedStore(
  "add-entry-continue",
  boolean,
  () => false,
);

/**
 * A store to hold an entry that should pre-fill the AddEntry modal.
 * Setting this to null means the next modal open will be a blank transaction.
 */
export const initial_entry = writable<Transaction | Balance | Note | null>(
  null,
);
