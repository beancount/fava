import type {
  Completion,
  CompletionResult,
  CompletionSource,
} from "@codemirror/autocomplete";
import { syntaxTree } from "@codemirror/language";
import { get as store_get } from "svelte/store";

import { accounts, currencies, links, payees, tags } from "../stores";
import { beancountSnippets } from "./beancount-snippets";

const undatedDirectives = ["option", "plugin", "include"];
const datedDirectives = [
  "*",
  "open",
  "close",
  "custom",
  "commodity",
  "balance",
  "pad",
  "note",
  "document",
  "price",
  "event",
  "query",
];

/** Get Completion objects from strings. */
const opts = (s: readonly string[]): Completion[] =>
  s.map((label) => ({ label }));

/** Generate completion result list for codemirror from strings. */
const res = (s: readonly string[], from: number): CompletionResult => ({
  options: opts(s),
  from,
});

export const beancountCompletion: CompletionSource = (context) => {
  const tag = context.matchBefore(/#[A-Za-z0-9\-_/.]*/);
  if (tag) {
    return {
      options: opts(store_get(tags)),
      from: tag.from + 1,
      validFor: /\S+/,
    };
  }

  const link = context.matchBefore(/\^[A-Za-z0-9\-_/.]*/);
  if (link) {
    return {
      options: opts(store_get(links)),
      from: link.from + 1,
      validFor: /\S+/,
    };
  }

  const indented = context.matchBefore(/^\s+[A-Z]\S*/);
  if (indented) {
    const indentation = indented.text.length - indented.text.trimStart().length;
    return {
      options: opts(store_get(accounts)),
      from: indented.from + indentation,
      validFor: /\S+/,
    };
  }

  const line = context.state.doc.lineAt(context.pos);
  if (context.matchBefore(/\d+/)) {
    return { options: beancountSnippets(), from: line.from };
  }

  const currentWord = context.matchBefore(/\S*/);
  if (currentWord?.from === line.from && line.length > 0) {
    return {
      options: opts(undatedDirectives),
      from: line.from,
      validFor: /\S+/,
    };
  }

  const tree = syntaxTree(context.state);
  const before = tree.resolve(context.pos, -1);
  // Node types of the last 4 nodes.
  const nodeTypesBefore = [
    before.name,
    before.prevSibling?.name,
    before.prevSibling?.prevSibling?.name,
    before.prevSibling?.prevSibling?.prevSibling?.name,
  ];
  type T = string | string[];
  // Check whether the previous nodes (up to 4) match the given types.
  const match = (...types: [T] | [T, T] | [T, T, T] | [T, T, T, T]): boolean =>
    types.every((t, i) => {
      const nodeType = nodeTypesBefore[i];
      return typeof t === "string"
        ? nodeType === t
        : t.some((n) => nodeType === n);
    });

  // complete payee after transaction flag.
  if (match("string", "flag")) {
    return res(store_get(payees), before.from + 1);
  }

  // complete directive names after a date.
  if (match("keyword", "date")) {
    return res(datedDirectives, before.from);
  }

  if (
    // account directly after one of these directives:
    match(
      ["ERROR", "account"],
      ["BALANCE", "CLOSE", "OPEN", "PAD", "NOTE", "DOCUMENT"],
      "date",
    ) ||
    // padding account
    match(["ERROR", "account"], "account", "PAD", "date")
  ) {
    return res(store_get(accounts), before.from);
  }

  if (
    // complete currencies after a number.
    match("ERROR", "number") ||
    // account currency
    match(["ERROR", "currency"], "account", "OPEN", "date") ||
    // price or commodity currency
    match(["ERROR", "currency"], ["COMMODITY", "PRICE"], "date")
  ) {
    return res(store_get(currencies), before.from);
  }

  return null;
};
