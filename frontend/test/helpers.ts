import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { ledgerDataValidator } from "../src/api/validators.ts";
import { parseJSON } from "../src/lib/json.ts";
import { ledgerData } from "../src/stores/index.ts";
import { current_url } from "../src/stores/url.ts";

/** Load the Python test snapshot output with the given name and parse as JSON. */
export async function loadJSONSnapshot(
  name: `${string}.json`,
): Promise<unknown> {
  const path = join(
    fileURLToPath(import.meta.url),
    "..",
    "..",
    "..",
    "tests",
    "__snapshots__",
    name,
  );
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
    current_url.set(
      new URL("http://localhost:5000/example-beancount-file/income_statement/"),
    );
    loaded = true;
  } catch (error: unknown) {
    console.error(error);
  }
}
