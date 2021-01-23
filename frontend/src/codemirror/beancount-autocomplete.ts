import { CompletionSource } from "@codemirror/autocomplete";
import { StreamLanguage } from "@codemirror/stream-parser";
import { get, Readable } from "svelte/store";

import { accounts, currencies, links, payees, tags } from "../stores";

import { beancountSnippets } from "./beancount-snippets";
import { beancountStreamParser } from "./beancount-stream-parser";

const undatedDirectives = ["option", "plugin", "include"];
const datedDirectives = [
  "*",
  "open",
  "close",
  "commodity",
  "balance",
  "pad",
  "note",
  "document",
  "price",
  "event",
  "query",
];

/** Generate completion result list for codemirror from strings. */
const res = (s: string[], from: number) => ({
  options: s.map((label) => ({ label })),
  from,
});

const lang = StreamLanguage.define(beancountStreamParser);

const directiveCompletions: Record<
  string,
  Array<Readable<string[]> | null> | undefined
> = {
  open: [accounts, currencies],
  close: [accounts],
  commodity: [currencies],
  balance: [accounts, null, currencies],
  pad: [accounts, accounts],
  note: [accounts],
  document: [accounts],
  price: [currencies, null, currencies],
};

export const beancountCompletion: CompletionSource = (context) => {
  const { state, pos } = context;
  const { doc } = state;

  const tag = context.matchBefore(/#[A-Za-z0-9\-_/.]*/);
  if (tag) {
    return res(get(tags), tag.from + 1);
  }

  const link = context.matchBefore(/\^[A-Za-z0-9\-_/.]*/);
  if (link) {
    return res(get(links), link.from + 1);
  }

  const indented = context.matchBefore(/^\s+[A-Z]\S*/);
  if (indented) {
    const indentation = indented.text.length - indented.text.trimLeft().length;
    return res(get(accounts), indented.from + indentation);
  }

  const line = doc.lineAt(pos);

  if (context.matchBefore(/\d+/)) {
    return { options: beancountSnippets(), from: line.from };
  }
  const currentWord = context.matchBefore(/\S*/);
  if (currentWord?.from === line.from && line.length > 0) {
    return res(undatedDirectives, line.from);
  }

  const lineContent = doc.sliceString(line.from, pos);
  const node = lang.parseString(lineContent).cursor();
  const tokens: { name: string; from: number; to: number }[] = [];
  while (node.next()) {
    if (node.name !== "invalid.special") {
      tokens.push({ name: node.name, from: node.from, to: node.to });
    }
  }
  if (tokens.length > 0) {
    const first = tokens[0];
    const last = tokens[tokens.length - 1];
    const lineFrom = line.from;
    // Dates have the 'number.special' token name
    if (first.name === "number.special" && line.length > last.to) {
      if (tokens.length === 1) {
        return res(datedDirectives, lineFrom + first.to + 1);
      }
      const directive = lineContent.slice(tokens[1].from, tokens[1].to);
      const compl = directiveCompletions[directive];
      if (compl) {
        const completions = compl[tokens.length - 2];
        if (completions) {
          return res(get(completions), lineFrom + last.to + 1);
        }
      }
      if (directive === "txn" || directive.length === 1) {
        if (tokens.length === 3 || last.name === "string.special") {
          return res(get(payees), lineFrom + last.from + 1);
        }
      }
    }
    if (last.name === "number" && line.length > last.to) {
      return res(get(currencies), lineFrom + last.to + 1);
    }
  }

  return null;
};
