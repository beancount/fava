import { deepEqual, equal, ok } from "node:assert/strict";
import { before, test } from "node:test";

import { get as store_get } from "svelte/store";

import { chart_context } from "../src/charts/context.ts";
import {
  currencies_scale,
  sunburst_scale,
  treemap_scale,
} from "../src/charts/helpers.ts";
import { Event, entryValidator } from "../src/entries/index.ts";
import { array } from "../src/lib/validation.ts";
import { conversions } from "../src/stores/chart.ts";
import { currencies, ledger_data } from "../src/stores/index.ts";
import { initialise_ledger_data, load_json_snapshot } from "./helpers.ts";

before(initialise_ledger_data);

test("validate ledger data", () => {
  const res = store_get(ledger_data);

  equal(res.accounts[0], "Liabilities:US:Chase:Slate");

  const $conversions = store_get(conversions);
  equal($conversions[0], "at_cost");

  deepEqual(store_get(treemap_scale).domain(), res.accounts);
  deepEqual(store_get(sunburst_scale).domain(), res.accounts);
  equal(
    store_get(sunburst_scale)("Liabilities:US:Chase:Slate"),
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
  deepEqual(store_get(currencies), all_currencies);
  // Operating currency first, then sorted
  deepEqual(store_get(currencies_scale).domain().slice(0, 3), [
    "USD",
    "ABC",
    "GLD",
  ]);

  deepEqual(store_get(chart_context).currencies, ["USD"]);
});

test("validate events", async () => {
  const data = await load_json_snapshot("test_json_api-test_api-events.json");
  const res = array(Event.validator)(data);
  equal(res.unwrap()[0]?.type, "employer");
});

test("validate journal", async () => {
  const data = await load_json_snapshot("test_json_api-test_api-journal.json");
  const res = array(entryValidator)(data);
  ok(res.is_ok);
  const entries = res.unwrap();
  equal(entries.length, 26);
});
