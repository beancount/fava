import { deepEqual } from "node:assert/strict";
import { test } from "node:test";

import { RawAmount } from "../src/entries/amount.ts";
import {
  Balance,
  EntryMetadata,
  Posting,
  Transaction,
} from "../src/entries/index.ts";
import { group_entries } from "../src/reports/import/group.ts";

function transaction(payee: string, accounts: string[], duplicate = false) {
  return new Transaction(
    new EntryMetadata(duplicate ? { __duplicate__: true } : {}),
    "2022-12-12",
    "",
    "*",
    payee,
    "",
    [],
    [],
    accounts.map((account) => new Posting(new EntryMetadata(), account, "")),
  );
}

const balance = new Balance(
  new EntryMetadata(),
  "2022-12-12",
  "",
  "Assets:Cash",
  new RawAmount("10", "USD"),
);

const entries = [
  transaction("Store", ["Assets:Cash", "Expenses:Food"], true),
  transaction("", ["Assets:Cash"]),
  balance,
  transaction("Store", ["Expenses:Food", "Assets:Cash"]),
];

test("group import entries by status", () => {
  deepEqual(group_entries(entries, "status"), [
    ["To import", [1, 2, 3]],
    ["Duplicates", [0]],
  ]);
  deepEqual(group_entries([balance], "status"), [["To import", [0]]]);
});

test("group import entries by accounts", () => {
  deepEqual(group_entries(entries, "accounts"), [
    ["Accounts: Assets:Cash, Expenses:Food", [0, 3]],
    ["Accounts: Assets:Cash", [1]],
    ["Balance", [2]],
  ]);
});

test("group import entries by payee", () => {
  deepEqual(group_entries(entries, "payee"), [
    ["Payee: 'Store'", [0, 3]],
    ["Payee: ''", [1]],
    ["Balance", [2]],
  ]);
});
