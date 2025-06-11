import { test } from "uvu";
import * as assert from "uvu/assert";

import {
  ancestors,
  get_internal_accounts,
  is_descendant,
  is_descendant_or_equal,
  leaf,
  parent,
} from "../src/lib/account";

test("account: split account names", () => {
  assert.equal(ancestors("Assets:Cash:Sub"), [
    "Assets",
    "Assets:Cash",
    "Assets:Cash:Sub",
  ]);
  assert.equal(ancestors("Assets:Cash"), ["Assets", "Assets:Cash"]);
  assert.equal(ancestors("Assets"), ["Assets"]);
  assert.equal(ancestors(""), []);

  assert.is(parent("Assets:Cash:Sub"), "Assets:Cash");
  assert.is(parent("Assets:Cash"), "Assets");
  assert.is(parent("Assets"), "");
  assert.is(parent(""), "");

  assert.is(leaf("asd:asdf"), "asdf");
  assert.is(leaf("asd"), "asd");
  assert.is(leaf(""), "");
});

test("account: get internal accounts", () => {
  assert.equal(
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
  assert.is(true, is_descendant_of_root("A"));
  assert.is(true, is_descendant_of_root("A:Test"));
  const is_descendant_of_assets = is_descendant_or_equal("Assets");
  assert.is(true, is_descendant_of_assets("Assets"));
  assert.is(true, is_descendant_of_assets("Assets:Cash"));
  assert.is(false, is_descendant_of_assets("AssetsOther"));
  assert.is(false, is_descendant_of_assets("Income:Other"));
  const is_descendant_of_assets_cash = is_descendant_or_equal("Assets:Cash");
  assert.is(true, is_descendant_of_assets_cash("Assets:Cash"));
  assert.is(false, is_descendant_of_assets_cash("Assets"));

  const is_true_descendant_of_root = is_descendant("");
  assert.is(true, is_true_descendant_of_root("A"));
  assert.is(true, is_true_descendant_of_root("A:Test"));
  assert.is(false, is_true_descendant_of_root(""));
  const is_true_descendant_of_assets = is_descendant("Assets");
  assert.is(false, is_true_descendant_of_assets("Assets"));
  assert.is(true, is_true_descendant_of_assets("Assets:Cash"));
});

test.run();
