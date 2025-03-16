import { test } from "uvu";
import assert from "uvu/assert";

import {
  Amount,
  Balance,
  Cost,
  EntryMetadata,
  entryValidator,
  Note,
  Transaction,
} from "../src/entries";
import { Position } from "../src/entries/position";
import { formatter_context } from "../src/format";

test("metadata: basic operations", () => {
  const meta = new EntryMetadata({ key: "value" });
  assert.not(meta.is_empty());
  assert.equal(meta.toJSON(), { key: "value" });
  assert.equal(meta.get("key"), "value");
  assert.equal(meta.get("nokey"), undefined);
  assert.equal(meta.entries(), [["key", "value"]]);

  const meta_empty = meta.delete("key");
  assert.ok(meta_empty.is_empty());

  const meta_added = meta.add();
  assert.equal(meta_added.entries(), [
    ["key", "value"],
    ["", ""],
  ]);

  const meta_updated = meta.update_key("key", "newkey");
  assert.equal(meta_updated.entries(), [["newkey", "value"]]);

  const meta_added_updated = meta_added.update_key("key", "newkey");
  assert.equal(meta_added_updated.entries(), [
    ["newkey", "value"],
    ["", ""],
  ]);
});

test("metadata: validate JSON with fallback", () => {
  const meta = EntryMetadata.validator({
    boolean: true,
    false: false,
    key: "value",
    number: 10,
    unsupported: [],
  }).unwrap();
  assert.equal(meta.entries(), [
    ["boolean", "TRUE"],
    ["false", "FALSE"],
    ["key", "value"],
    ["number", "10"],
    ["unsupported", "Unsupported metadata value"],
  ]);
});

test("metadata: entries as strings", () => {
  const meta = new EntryMetadata({
    boolean: true,
    false: false,
    key: "value",
    number: 10,
  });
  assert.equal(meta.entries(), [
    ["boolean", "TRUE"],
    ["false", "FALSE"],
    ["key", "value"],
    ["number", "10"],
  ]);
});

test("metadata: set from string", () => {
  const meta = new EntryMetadata();
  assert.equal(meta.set_string("key", "TRUE").get("key"), true);
  assert.equal(meta.set_string("key", "true").get("key"), "true");
  assert.equal(meta.set_string("key", "string").get("key"), "string");
  assert.equal(meta.set_string("key", "FALSE").get("key"), false);
});

test("metadata: get filename and lineno", () => {
  const meta = new EntryMetadata();
  const meta_with_position = new EntryMetadata({
    filename: "/path",
    lineno: 100,
  });
  assert.equal(meta_with_position.filename, "/path");
  assert.equal(meta_with_position.lineno, "100");
  assert.equal(meta.filename, "");
  assert.equal(meta.lineno, "");
});

test("create empty entries on a date", () => {
  assert.instance(new Balance("2012-12-12"), Balance);
  assert.instance(new Note("2012-12-12"), Note);
  assert.instance(new Transaction("2012-12-12"), Transaction);
});

test("create amounts, cost, and positions from JSON data", () => {
  const amt = Amount.validator({ number: 10, currency: "EUR" }).unwrap();
  assert.is(amt.number, 10);
  assert.instance(amt, Amount);

  const cost = Cost.validator({
    number: 10,
    currency: "EUR",
    date: "2012-12-12",
    label: "a label",
  }).unwrap();
  assert.is(cost.number, 10);
  assert.instance(cost, Cost);

  const position = Position.validator({
    units: { number: 10, currency: "EUR" },
  }).unwrap();
  assert.is(position.units.number, 10);
  assert.is(position.cost, null);
  assert.instance(position, Position);

  const ctx = formatter_context(false, null, {});
  assert.equal(amt.str(ctx), "10.00 EUR");
  assert.equal(cost.str(ctx), '10.00 EUR, 2012-12-12, "a label"');
});

test("create entries from JSON data", () => {
  const balance = entryValidator({
    t: "Balance",
    meta: { filename: "/home/test/test.beancount", lineno: 1 },
    date: "2022-12-12",
    account: "Expenses:Food",
    amount: { number: "10", currency: "USD" },
  }).unwrap();
  assert.instance(balance, Balance);

  const note = entryValidator({
    t: "Note",
    meta: { filename: "/home/test/test.beancount", lineno: 1 },
    date: "2022-12-12",
    account: "Expenses:Food",
    comment: "Some note for the expenses account",
  }).unwrap();
  assert.instance(note, Note);

  const transaction = entryValidator({
    t: "Transaction",
    meta: { filename: "/home/test/test.beancount", lineno: 1 },
    date: "2022-12-12",
    flag: "*",
    payee: "Some Store",
    narration: "Bought food",
    tags: [],
    links: [],
    postings: [
      { account: "Expenses:Food", amount: "", meta: {} },
      { account: "Assets:Cash", amount: "-5.15 EUR", meta: null },
      { account: "Assets:Cash", amount: "-5.15 EUR" },
    ],
  }).unwrap();
  assert.instance(transaction, Transaction);
});

test.run();
