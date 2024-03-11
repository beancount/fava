import { get as store_get } from "svelte/store";
import { test } from "uvu";
import assert from "uvu/assert";

import { getAPIValidators, ledgerDataValidator } from "../src/api/validators";
import { chartContext } from "../src/charts/context";
import {
  currenciesScale,
  sunburstScale,
  treemapScale,
} from "../src/charts/helpers";
import { getUrlPath } from "../src/helpers";
import { base_url, currencies, ledgerData } from "../src/stores";
import { conversions } from "../src/stores/chart";

import { loadJSONSnapshot } from "./helpers";

test("validate ledger data", async () => {
  const data = await loadJSONSnapshot(
    "test_internal_api-test_get_ledger_data.json",
  );
  const res = ledgerDataValidator(data).unwrap();
  assert.equal(res.accounts[0], "Liabilities:US:Chase:Slate");

  ledgerData.set(res);

  assert.equal(store_get(conversions)[0], "at_cost");

  assert.equal(store_get(treemapScale).domain(), res.accounts);
  assert.equal(store_get(sunburstScale).domain(), res.accounts);
  assert.equal(
    store_get(sunburstScale)("Liabilities:US:Chase:Slate"),
    "rgb(126, 174, 253)",
  );

  const base = store_get(base_url);
  assert.equal(getUrlPath({ pathname: `${base}/asdf` }), "/asdf");
  assert.equal(
    getUrlPath({ pathname: `${base}/${encodeURI("Ä€/asdf")}` }),
    "/Ä€/asdf",
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
