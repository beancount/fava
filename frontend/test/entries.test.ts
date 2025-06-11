import { test } from "uvu";
import * as assert from "uvu/assert";

import {
  Amount,
  Balance,
  Cost,
  Document,
  EntryMetadata,
  entryValidator,
  Note,
  Posting,
  Transaction,
} from "../src/entries/index";
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

test("postings", () => {
  const posting = Posting.empty();
  assert.instance(posting, Posting);
  assert.ok(posting.is_empty());

  assert.equal(posting.account, "");
  const modified = posting.set("account", "Assets");
  assert.equal(posting.account, "");
  assert.equal(modified.account, "Assets");
});

test("create empty entries on a date", () => {
  assert.instance(Balance.empty("2012-12-12"), Balance);
  assert.instance(Note.empty("2012-12-12"), Note);
  assert.instance(Transaction.empty("2012-12-12"), Transaction);
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

test("entries: create changed copies", () => {
  const balance = Balance.empty("2012-12-12");
  assert.ok(balance instanceof Balance);
  const balance_changed = balance.set("account", "Assets:Cash");
  assert.equal(balance_changed.account, "Assets:Cash");
  assert.equal(balance.account, "");

  const balance_with_meta = balance.set_meta("key", "value");
  assert.equal(balance.meta.get("key"), undefined);
  assert.equal(balance_with_meta.meta.get("key"), "value");

  assert.not(balance.is_duplicate());
  assert.ok(balance.set_meta("__duplicate__", true).is_duplicate());
  assert.ok(balance.set_meta("__duplicate__", "asdfasdf").is_duplicate());
});

test("create entries from JSON data", () => {
  const balance = entryValidator({
    t: "Balance",
    meta: { filename: "/home/test/test.beancount", lineno: 1 },
    date: "2022-12-12",
    entry_hash: "ENTRY_HASH",
    account: "Expenses:Food",
    amount: { number: "10", currency: "USD" },
  }).unwrap();
  assert.instance(balance, Balance);

  const doc = entryValidator({
    t: "Document",
    meta: { filename: "/home/test/test.beancount", lineno: 1 },
    date: "2022-12-12",
    entry_hash: "ENTRY_HASH",
    account: "Expenses:Food",
    filename: "/tmp/some/path",
    tags: [],
    links: [],
  }).unwrap();
  assert.instance(doc, Document);

  const note = entryValidator({
    t: "Note",
    meta: { filename: "/home/test/test.beancount", lineno: 1 },
    date: "2022-12-12",
    entry_hash: "ENTRY_HASH",
    account: "Expenses:Food",
    comment: "Some note for the expenses account",
  }).unwrap();
  assert.instance(note, Note);

  const raw = {
    t: "Transaction",
    meta: { filename: "/home/test/test.beancount", lineno: 1 },
    date: "2022-12-12",
    entry_hash: "ENTRY_HASH",
    flag: "*",
    payee: "Some Store",
    narration: "Bought food",
    tags: [],
    links: [],
    postings: [
      { account: "Expenses:Food", amount: "", meta: {} },
      { account: "Assets:Cash", amount: "-5.15 EUR", meta: {} },
      { account: "Assets:Cash", amount: "-5.15 EUR", meta: {} },
    ],
  };
  const transaction = entryValidator(raw).unwrap();
  assert.ok(transaction instanceof Transaction);
  const json: unknown = JSON.parse(JSON.stringify(transaction));
  assert.equal(Object.keys(raw), Object.keys(json as Record<string, unknown>));
  assert.equal(raw, json);

  const raw_with_null_meta_postings = {
    t: "Transaction",
    meta: { filename: "/home/test/test.beancount", lineno: 1 },
    date: "2022-12-12",
    entry_hash: "ENTRY_HASH",
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
  };
  const transaction_with_null_meta = entryValidator(
    raw_with_null_meta_postings,
  ).unwrap();
  assert.ok(transaction_with_null_meta instanceof Transaction);
});

test("transaction: combine narration, tags, and links", () => {
  const txn = Transaction.empty("2022-12-12");
  assert.equal(txn.get_narration_tags_links(), "");

  const basic_narration = txn.set("narration", "a narration");
  assert.equal(basic_narration.get_narration_tags_links(), "a narration");
  const narration_and_tag = basic_narration.set("tags", ["tag"]);
  assert.equal(
    narration_and_tag.get_narration_tags_links(),
    "a narration #tag",
  );
  const narration_tag_and_link = narration_and_tag.set("links", ["link"]);
  assert.equal(
    narration_tag_and_link.get_narration_tags_links(),
    "a narration #tag ^link",
  );

  const parsed = txn.set_narration_tags_links("a narration   #tag ^link");
  assert.equal(parsed.narration, "a narration");
  assert.equal(parsed.tags, ["tag"]);
  assert.equal(parsed.links, ["link"]);
});

test.run();
