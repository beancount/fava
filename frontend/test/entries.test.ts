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
  assert.instance(create("Balance", "2012-12-12"), Balance);
  assert.instance(create("Note", "2012-12-12"), Note);
  assert.instance(create("Transaction", "2012-12-12"), Transaction);
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

  assert.instance(txn.unwrap(), Transaction);

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

  assert.instance(note.unwrap(), Note);
});

test.run();
