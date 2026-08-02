import { local_storage_synced_store } from "../lib/store.ts";
import { boolean } from "../lib/validation.ts";

/** Whether to reload after saving an entry in the slice editor. */
export const reload_after_saving_entry_slice = local_storage_synced_store(
  "reload-after-saving-entry-slice",
  boolean,
  () => true,
);

/** Whether to continue (and add another entry) after adding an entry in the AddEntry dialog. */
export const add_entry_continue = local_storage_synced_store(
  "add-entry-continue",
  boolean,
  () => false,
);
