import { deepEqual, equal, ok } from "node:assert/strict";
import { test } from "node:test";

import {
  CompletionContext,
  type CompletionResult,
  insertCompletionText,
} from "@codemirror/autocomplete";
import { EditorState } from "@codemirror/state";

import { complete_bql } from "../src/codemirror/bql-autocomplete.ts";
import { bql_language_support } from "../src/codemirror/bql-language.ts";

const payees = [
  "Farmer Fresh",
  "Acme, Inc.",
  "A+B",
  "Shop (West",
  String.raw`C:\Temp`,
  "O'Brien",
  'Acme "West"',
];

function complete(marked_doc: string) {
  const pos = marked_doc.indexOf("|");
  ok(pos >= 0);
  equal(pos, marked_doc.lastIndexOf("|"));
  const state = EditorState.create({
    doc: marked_doc.replace("|", ""),
    extensions: [bql_language_support],
    selection: { anchor: pos },
  });
  return {
    pos,
    result: complete_bql(new CompletionContext(state, pos, false), payees),
    state,
  };
}

function labels(result: CompletionResult): string[] {
  return result.options.map(({ label }) => label);
}

function accept(marked_doc: string, label: string): string {
  const { pos, result, state } = complete(marked_doc);
  ok(result);
  const option = result.options.find((candidate) => candidate.label === label);
  ok(option);
  const apply = option.apply ?? option.label;
  if (typeof apply !== "string") {
    throw new TypeError("Expected a string completion");
  }
  const transaction = state.update(
    insertCompletionText(state, apply, result.from, result.to ?? pos),
  );
  return transaction.state.doc.toString();
}

test("BQL autocomplete suggests payees in equality comparisons", () => {
  for (const operator of ["=", "!="]) {
    const { result } = complete(
      `SELECT date WHERE PAYEE ${operator} "Far|mer Fresh"`,
    );
    ok(result);
    deepEqual(
      labels(result),
      payees.filter((payee) => !payee.includes('"')),
    );
  }
});

test("BQL autocomplete supports single-quoted payee values", () => {
  const { result } = complete("SELECT date WHERE payee = 'Ac|me'");
  ok(result);
  deepEqual(
    labels(result),
    payees.filter((payee) => !payee.includes("'")),
  );
});

test("BQL autocomplete replaces the complete string value", () => {
  equal(
    accept('SELECT date WHERE payee = "Far|mer Fresh"', "Farmer Fresh"),
    'SELECT date WHERE payee = "Farmer Fresh"',
  );
});

test("BQL autocomplete escapes payees used as regular expressions", () => {
  for (const operator of ["~", "!~"]) {
    equal(
      accept(`SELECT date WHERE payee ${operator} "|"`, "A+B"),
      `SELECT date WHERE payee ${operator} "A\\+B"`,
    );
    equal(
      accept(`SELECT date WHERE payee ${operator} "|"`, "Shop (West"),
      `SELECT date WHERE payee ${operator} "Shop \\(West"`,
    );
    equal(
      accept(`SELECT date WHERE payee ${operator} "|"`, String.raw`C:\Temp`),
      String.raw`SELECT date WHERE payee ${operator} "C:\\Temp"`,
    );
  }
});

test("BQL equality autocomplete preserves backslashes", () => {
  equal(
    accept('SELECT date WHERE payee = "|"', String.raw`C:\Temp`),
    String.raw`SELECT date WHERE payee = "C:\Temp"`,
  );
});

test("BQL autocomplete only suggests payees in payee value contexts", () => {
  for (const query of [
    'SELECT date WHERE narration = "Far|"',
    'SELECT date WHERE some_payee = "Far|"',
    'SELECT date WHERE payee =~ "Far|"',
    'SELECT date WHERE payee ?~ "Far|"',
    "SELECT 'payee = \"Far|\"'",
    'SELECT date WHERE payee = "Far"|',
    'SELECT date; payee = "Far|"',
    'SELECT date /* payee = "Far|" */ WHERE true',
    'SELECT date /* comment\n payee = "Far|"\n */ WHERE true',
  ]) {
    const { result } = complete(query);
    equal(
      result ? labels(result).some((label) => payees.includes(label)) : false,
      false,
    );
  }
});

test("BQL autocomplete preserves syntax completions", () => {
  const command = complete("sel|").result;
  ok(command);
  equal(command.from, 0);
  equal(
    command.options.some(({ label }) => label === "select"),
    true,
  );

  const syntax = complete("select da|").result;
  ok(syntax);
  equal(syntax.from, 7);
  equal(
    syntax.options.some(({ label }) => label === "date"),
    true,
  );

  const after_string = complete('select "value" as na|').result;
  ok(after_string);
  equal(after_string.from, 18);
  equal(
    after_string.options.some(({ label }) => label === "name"),
    true,
  );
});
