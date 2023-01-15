import { test } from "uvu";
import assert from "uvu/assert";

import {
  Balance,
  create,
  entryValidator,
  Note,
  Transaction,
} from "../src/entries";

test("create entries from scratch", () => {
  assert.instance(create("Balance"), Balance);
  assert.instance(create("Note"), Note);
  assert.instance(create("Transaction"), Transaction);
});

test("create entries from JSON data", () => {
  const txn = entryValidator({
    type: "Transaction",
    meta: {
      filename: "/home/test/test.beancount",
      lineno: 1,
    },
    date: "2022-12-12",
    flag: "*",
    payee: "Some Store",
    narration: "Bought food",
    tags: [],
    links: [],
    postings: [
      {
        account: "Expenses:Food",
        amount: "",
      },
      {
        account: "Assets:Cash",
        amount: "-5.15 EUR",
      },
    ],
  });

  assert.is(txn.success, true);
  assert.instance(txn.value, Transaction);

  const note = entryValidator({
    type: "Note",
    meta: {
      filename: "/home/test/test.beancount",
      lineno: 1,
    },
    date: "2022-12-12",
    account: "Expenses:Food",
    comment: "Some note for the expenses account",
  });

  assert.is(note.success, true);
  assert.instance(note.value, Note);
});

test.run();
