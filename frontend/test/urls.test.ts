import { get as store_get } from "svelte/store";
import { test } from "uvu";
import assert from "uvu/assert";

import { getUrlPath, urlForAccount, urlForInternal } from "../src/helpers";
import { base_url } from "../src/stores";
import { initialiseLedgerData } from "./helpers";

test.before(initialiseLedgerData);

test("get URL", () => {
  const searchParams = new URLSearchParams({ time: "2000" });
  assert.equal(
    urlForInternal("/base/", searchParams, "report", {
      asdf: 10,
      none: undefined,
    }),
    "/base/report?time=2000&asdf=10",
  );
  assert.equal(searchParams.get("asdf"), null);
});

test("get path for account", () => {
  const $urlForAccount = store_get(urlForAccount);
  assert.equal($urlForAccount("Assets"), "/long-example/account/Assets/");
});

test("extract relative path from URL", () => {
  const $base_url = store_get(base_url);
  assert.equal($base_url, "/long-example/");
  assert.equal(getUrlPath({ pathname: "/example/asdf" }), null);
  assert.equal(getUrlPath({ pathname: "/long-example/asdf" }), "asdf");
  assert.equal(encodeURI("Ä€/asdf"), "%C3%84%E2%82%AC/asdf");
  assert.equal(
    getUrlPath({ pathname: "/long-example/%C3%84%E2%82%AC/asdf" }),
    "Ä€/asdf",
  );
});

test.run();
