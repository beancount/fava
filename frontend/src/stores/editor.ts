import { localStorageSyncedStore } from "../lib/store";
import { boolean } from "../lib/validation";

/** Whether to reload after saving an entry in the slice editor. */
export const reloadAfterSavingEntrySlice = localStorageSyncedStore(
  "reload-after-saving-entry-slice",
  boolean,
  () => true
);
