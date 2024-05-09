import { test } from "uvu";
import assert from "uvu/assert";

import {
  Amount,
  Balance,
  entryValidator,
  Note,
  Transaction,
} from "../src/entries";

test("create entries from scratch", () => {
  assert.instance(new Balance("2012-12-12"), Balance);
  assert.instance(new Note("2012-12-12"), Note);
  assert.instance(new Transaction("2012-12-12"), Transaction);
});

test("create amounts, cost, and positions from JSON data", () => {
  const amt = Amount.validator({ number: 10, currency: "EUR" }).unwrap();
  assert.is(amt.number, 10);
  assert.instance(amt, Amount);
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
