import { get as store_get } from "svelte/store";
import { test } from "uvu";
import assert from "uvu/assert";

import { getAPIValidators } from "../src/api/validators";
import { chartContext } from "../src/charts/context";
import {
  currenciesScale,
  sunburstScale,
  treemapScale,
} from "../src/charts/helpers";
import { currencies, ledgerData } from "../src/stores";
import { conversions } from "../src/stores/chart";
import { initialiseLedgerData, loadJSONSnapshot } from "./helpers";

test.before(initialiseLedgerData);

test("validate ledger data", () => {
  const res = store_get(ledgerData);

  assert.equal(res.accounts[0], "Liabilities:US:Chase:Slate");

  const $conversions = store_get(conversions);
  assert.equal($conversions[0], "at_cost");

  assert.equal(store_get(treemapScale).domain(), res.accounts);
  assert.equal(store_get(sunburstScale).domain(), res.accounts);
  assert.equal(
    store_get(sunburstScale)("Liabilities:US:Chase:Slate"),
    "rgb(126, 174, 253)",
  );

  const all_currencies = [
    "USD",
    "VACHR",
    "IRAUSD",
    "VBMPX",
    "RGAGX",
    "GLD",
    "VEA",
    "VHT",
    "ITOT",
    "ABC",
    "XYZ",
  ];
  assert.equal(store_get(currencies), all_currencies);
  // Operating currency first, then sorted
  assert.equal(store_get(currenciesScale).domain().slice(0, 3), [
    "USD",
    "ABC",
    "GLD",
  ]);

  assert.equal(store_get(chartContext).currencies, ["USD"]);
});

test("validate events", async () => {
  const data = await loadJSONSnapshot("test_json_api-test_api-events.json");
  const res = getAPIValidators.events(data);
  assert.equal(res.unwrap()[0]?.type, "employer");
});

test.run();
