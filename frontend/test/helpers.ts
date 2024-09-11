import { readFile } from "fs/promises";
import { join } from "path";

import { ledgerDataValidator } from "../src/api/validators";
import { parseJSON } from "../src/lib/json";
import { ledgerData } from "../src/stores";

/** Load the Python test snapshot output with the given name and parse as JSON. */
export async function loadJSONSnapshot(
  name: `${string}.json`,
): Promise<unknown> {
  const path = join(__dirname, "..", "..", "tests", "__snapshots__", name);
  return parseJSON(await readFile(path, "utf8")).unwrap();
}

let loaded = false;

/** Load the ledgerData (of the long-example file. */
export async function initialiseLedgerData(): Promise<void> {
  if (loaded) {
    return;
  }
  try {
    const data = await loadJSONSnapshot(
      "test_internal_api-test_get_ledger_data.json",
    );
    const res = ledgerDataValidator(data).unwrap();
    ledgerData.set(res);
    loaded = true;
  } catch (error: unknown) {
    console.error(error);
  }
}
