import { local_storage_synced_store } from "../lib/store.ts";
import { constants } from "../lib/validation.ts";
import type { ImportGrouping } from "../reports/import/group.ts";

/** How to group the entries in the import dialog. */
export const import_grouping = local_storage_synced_store<ImportGrouping>(
  "import-grouping",
  constants("status", "accounts", "payee"),
  () => "status",
);
