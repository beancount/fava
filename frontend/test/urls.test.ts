import { equal, ok } from "node:assert/strict";
import { test } from "node:test";

import { get as store_get } from "svelte/store";

import { getUrlPath, urlForAccount, urlForInternal } from "../src/helpers.ts";
import { base_url } from "../src/stores/index.ts";
import { initialiseLedgerData } from "./helpers.ts";

test.before(initialiseLedgerData);

test("get URL", () => {
  const searchParams = new URLSearchParams({ time: "2000" });
  equal(
    urlForInternal("/base/", searchParams, "report", {
      asdf: 10,
      none: undefined,
    }),
    "/base/report?time=2000&asdf=10",
  );
  equal(searchParams.get("asdf"), null);
});

test("get path for account", () => {
  const $urlForAccount = store_get(urlForAccount);
  equal($urlForAccount("Assets"), "/long-example/account/Assets/");
});

test("extract relative path from URL", () => {
  const $base_url = store_get(base_url);
  equal($base_url, "/long-example/");
  ok(getUrlPath({ pathname: "/example/asdf" }).is_err);
  equal(getUrlPath({ pathname: "/long-example/asdf" }).unwrap(), "asdf");
  equal(encodeURI("Ä€/asdf"), "%C3%84%E2%82%AC/asdf");
  equal(
    getUrlPath({ pathname: "/long-example/%C3%84%E2%82%AC/asdf" }).unwrap(),
    "Ä€/asdf",
  );
});
