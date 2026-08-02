import { equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { get as store_get } from "svelte/store";

import {
  get_url_path,
  url_for_account,
  url_for_internal,
} from "../src/helpers.ts";
import { base_url } from "../src/stores/index.ts";
import { initialise_ledger_data } from "./helpers.ts";

test.before(initialise_ledger_data);

test("get URL", () => {
  const search_params = new URLSearchParams({ time: "2000" });
  equal(
    url_for_internal("/base/", search_params, "report", {
      asdf: 10,
      none: undefined,
    }),
    "/base/report?time=2000&asdf=10",
  );
  equal(search_params.get("asdf"), null);
});

test("get path for account", () => {
  const $url_for_account = store_get(url_for_account);
  equal($url_for_account("Assets"), "/long-example/account/Assets/");
});

test("extract relative path from URL", () => {
  const $base_url = store_get(base_url);
  equal($base_url, "/long-example/");
  ok(get_url_path({ pathname: "/example/asdf" }).is_err);
  equal(get_url_path({ pathname: "/long-example/asdf" }).unwrap(), "asdf");
  equal(encodeURI("Ä€/asdf"), "%C3%84%E2%82%AC/asdf");
  equal(
    get_url_path({ pathname: "/long-example/%C3%84%E2%82%AC/asdf" }).unwrap(),
    "Ä€/asdf",
  );
});
