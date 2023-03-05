import { readFile } from "fs/promises";
import { join } from "path";

import { test } from "uvu";
import assert from "uvu/assert";

import { getAPIValidators, ledgerDataValidator } from "../src/api/validators";

function loadSnapshot(name: string): Promise<string> {
  const path = join(__dirname, "..", "..", "tests", "__snapshots__", name);
  return readFile(path, "utf8");
}

test("validate ledger data", async () => {
  const data = await loadSnapshot("test_internal_api.py-test_get_ledger_data");
  const res = ledgerDataValidator(JSON.parse(data));
  assert.ok(res.success);
  assert.equal(res.value.accounts[0], "Liabilities:US:Chase:Slate");
});

test("validate events", async () => {
  const data = await loadSnapshot("test_json_api.py-test_api_events");
  const res = getAPIValidators.events(JSON.parse(data));
  assert.ok(res.success);
});

test.run();
