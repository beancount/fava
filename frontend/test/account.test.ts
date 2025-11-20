import { deepEqual, equal } from "node:assert/strict";
import { test } from "node:test";

import {
  ancestors,
  get_internal_accounts,
  is_descendant,
  is_descendant_or_equal,
  leaf,
  parent,
} from "../src/lib/account.ts";

test("account: split account names", () => {
  deepEqual(ancestors("Assets:Cash:Sub"), [
    "Assets",
    "Assets:Cash",
    "Assets:Cash:Sub",
  ]);
  deepEqual(ancestors("Assets:Cash"), ["Assets", "Assets:Cash"]);
  deepEqual(ancestors("Assets"), ["Assets"]);
  deepEqual(ancestors(""), []);

  equal(parent("Assets:Cash:Sub"), "Assets:Cash");
  equal(parent("Assets:Cash"), "Assets");
  equal(parent("Assets"), "");
  equal(parent(""), "");

  equal(leaf("asd:asdf"), "asdf");
  equal(leaf("asd"), "asd");
  equal(leaf(""), "");
});

test("account: get internal accounts", () => {
  deepEqual(
    get_internal_accounts([
      "Assets:Cash:Sub",
      "Income:Something",
      "Income:Something:Subaccount",
    ]),
    ["Assets", "Assets:Cash", "Income", "Income:Something"],
  );
});

test("account: check whether account is descendant of another", () => {
  const is_descendant_of_root = is_descendant_or_equal("");
  equal(true, is_descendant_of_root("A"));
  equal(true, is_descendant_of_root("A:Test"));
  const is_descendant_of_assets = is_descendant_or_equal("Assets");
  equal(true, is_descendant_of_assets("Assets"));
  equal(true, is_descendant_of_assets("Assets:Cash"));
  equal(false, is_descendant_of_assets("AssetsOther"));
  equal(false, is_descendant_of_assets("Income:Other"));
  const is_descendant_of_assets_cash = is_descendant_or_equal("Assets:Cash");
  equal(true, is_descendant_of_assets_cash("Assets:Cash"));
  equal(false, is_descendant_of_assets_cash("Assets"));

  const is_true_descendant_of_root = is_descendant("");
  equal(true, is_true_descendant_of_root("A"));
  equal(true, is_true_descendant_of_root("A:Test"));
  equal(false, is_true_descendant_of_root(""));
  const is_true_descendant_of_assets = is_descendant("Assets");
  equal(false, is_true_descendant_of_assets("Assets"));
  equal(true, is_true_descendant_of_assets("Assets:Cash"));
});
