import { todayAsString } from "../format";
import { localStorageSyncedStore } from "../lib/store";
import { boolean, string } from "../lib/validation";

/** Whether to reload after saving an entry in the slice editor. */
export const reloadAfterSavingEntrySlice = localStorageSyncedStore(
  "reload-after-saving-entry-slice",
  boolean,
  () => true
);

/** Whether to continue (and add another entry) after adding an entry in the AddEntry dialog. */
export const addEntryContinue = localStorageSyncedStore(
  "add-entry-continue",
  boolean,
  () => false
);

/** Date of last item added in the AddEntry dialog. */
export const addEntryLastDate = localStorageSyncedStore(
  "add-entry-last-date",
  string,
  () => todayAsString()
);
