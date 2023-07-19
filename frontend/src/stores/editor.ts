import { localStorageSyncedStore } from "../lib/store";
import { boolean } from "../lib/validation";

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
