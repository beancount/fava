import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

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
} from "../src/entries/index.ts";
import { Position } from "../src/entries/position.ts";
import { formatter_context } from "../src/format.ts";

test("metadata: basic operations", () => {
  const meta = new EntryMetadata({ key: "value" });
  equal(meta.is_empty(), false);
  deepEqual(meta.toJSON(), { key: "value" });
  equal(meta.get("key"), "value");
  equal(meta.get("nokey"), undefined);
  deepEqual(meta.entries(), [["key", "value"]]);

  const meta_empty = meta.delete("key");
  ok(meta_empty.is_empty());

  const meta_added = meta.add();
  deepEqual(meta_added.entries(), [
    ["key", "value"],
    ["", ""],
  ]);

  const meta_updated = meta.update_key("key", "newkey");
  deepEqual(meta_updated.entries(), [["newkey", "value"]]);

  const meta_added_updated = meta_added.update_key("key", "newkey");
  deepEqual(meta_added_updated.entries(), [
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
  deepEqual(meta.entries(), [
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
  deepEqual(meta.entries(), [
    ["boolean", "TRUE"],
    ["false", "FALSE"],
    ["key", "value"],
    ["number", "10"],
  ]);
});

test("metadata: set from string", () => {
  const meta = new EntryMetadata();
  equal(meta.set_string("key", "TRUE").get("key"), true);
  equal(meta.set_string("key", "true").get("key"), "true");
  equal(meta.set_string("key", "string").get("key"), "string");
  equal(meta.set_string("key", "FALSE").get("key"), false);
});

test("metadata: get filename and lineno", () => {
  const meta = new EntryMetadata();
  const meta_with_position = new EntryMetadata({
    filename: "/path",
    lineno: 100,
  });
  equal(meta_with_position.filename, "/path");
  equal(meta_with_position.lineno, "100");
  equal(meta.filename, "");
  equal(meta.lineno, "");
});

test("postings", () => {
  const posting = Posting.empty();
  ok(posting instanceof Posting);
  ok(posting.is_empty());

  equal(posting.account, "");
  const modified = posting.set("account", "Assets");
  equal(posting.account, "");
  equal(modified.account, "Assets");
});

test("create empty entries on a date", () => {
  ok(Balance.empty("2012-12-12") instanceof Balance);
  ok(Note.empty("2012-12-12") instanceof Note);
  ok(Transaction.empty("2012-12-12") instanceof Transaction);
});

test("create amounts, cost, and positions from JSON data", () => {
  const amt = Amount.validator({ number: 10, currency: "EUR" }).unwrap();
  equal(amt.number, 10);
  ok(amt instanceof Amount);

  const cost = Cost.validator({
    number: 10,
    currency: "EUR",
    date: "2012-12-12",
    label: "a label",
  }).unwrap();
  equal(cost.number, 10);
  ok(cost instanceof Cost);

  const position = Position.validator({
    units: { number: 10, currency: "EUR" },
  }).unwrap();
  equal(position.units.number, 10);
  equal(position.cost, null);
  ok(position instanceof Position);

  const ctx = formatter_context(false, null, {});
  equal(amt.str(ctx), "10.00 EUR");
  equal(cost.str(ctx), '10.00 EUR, 2012-12-12, "a label"');
});

test("entries: create changed copies", () => {
  const balance = Balance.empty("2012-12-12");
  ok(balance instanceof Balance);
  const balance_changed = balance.set("account", "Assets:Cash");
  equal(balance_changed.account, "Assets:Cash");
  equal(balance.account, "");

  const balance_with_meta = balance.set_meta("key", "value");
  equal(balance.meta.get("key"), undefined);
  equal(balance_with_meta.meta.get("key"), "value");

  equal(balance.is_duplicate(), false);
  ok(balance.set_meta("__duplicate__", true).is_duplicate());
  ok(balance.set_meta("__duplicate__", "asdfasdf").is_duplicate());
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
  ok(balance instanceof Balance);

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
  ok(doc instanceof Document);

  const note = entryValidator({
    t: "Note",
    meta: { filename: "/home/test/test.beancount", lineno: 1 },
    date: "2022-12-12",
    entry_hash: "ENTRY_HASH",
    account: "Expenses:Food",
    comment: "Some note for the expenses account",
  }).unwrap();
  ok(note instanceof Note);

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
  ok(transaction instanceof Transaction);
  const json: unknown = JSON.parse(JSON.stringify(transaction));
  deepEqual(Object.keys(raw), Object.keys(json as Record<string, unknown>));
  deepEqual(raw, json);

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
  ok(transaction_with_null_meta instanceof Transaction);
});

test("transaction: combine narration, tags, and links", () => {
  const txn = Transaction.empty("2022-12-12");
  equal(txn.get_narration_tags_links(), "");

  const basic_narration = txn.set("narration", "a narration");
  equal(basic_narration.get_narration_tags_links(), "a narration");
  const narration_and_tag = basic_narration.set("tags", ["tag"]);
  equal(narration_and_tag.get_narration_tags_links(), "a narration #tag");
  const narration_tag_and_link = narration_and_tag.set("links", ["link"]);
  equal(
    narration_tag_and_link.get_narration_tags_links(),
    "a narration #tag ^link",
  );

  const parsed = txn.set_narration_tags_links("a narration   #tag ^link");
  equal(parsed.narration, "a narration");
  deepEqual(parsed.tags, ["tag"]);
  deepEqual(parsed.links, ["link"]);
});
