import { CompletionSource } from "@codemirror/autocomplete";
import { StreamLanguage } from "@codemirror/stream-parser";

import { getCompletion } from "../stores";

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

const opts = (s: string[]) => s.map((label) => ({ label }));

const lang = StreamLanguage.define(beancountStreamParser);

export const beancountCompletion: CompletionSource = (context) => {
  const { state, pos } = context;
  const { doc } = state;
  const line = doc.lineAt(pos);

  const tag = context.matchBefore(/#[A-Za-z0-9\-_/.]*/);
  if (tag) {
    return { options: opts(getCompletion("tags")), from: tag.from + 1 };
  }

  const link = context.matchBefore(/\^[A-Za-z0-9\-_/.]*/);
  if (link) {
    return { options: opts(getCompletion("links")), from: link.from + 1 };
  }

  const indented = context.matchBefore(/^\s+[A-Z]\S*/);
  if (indented) {
    const indentation = indented.text.length - indented.text.trimLeft().length;
    return {
      options: opts(getCompletion("accounts")),
      from: indented.from + indentation,
    };
  }

  const currentWord = context.matchBefore(/\S*/);
  if (currentWord?.from === line.from && line.length > 0) {
    return { options: opts(undatedDirectives), from: line.from };
  }

  const node = lang.parseString(doc.sliceString(line.from, pos)).cursor();
  const tokens: { name: string; from: number; to: number }[] = [];
  while (node.next()) {
    tokens.push({ name: node.name, from: node.from, to: node.to });
  }
  // console.log(tokens)
  if (tokens.length > 0) {
    const first = tokens[0];
    // Dates have the 'number.special' token name
    if (first.name === "number.special" && line.length > first.to) {
      return { options: opts(datedDirectives), from: first.to + 1 };
    }
  }

  return null;
};

/*
const directiveCompletions: Record<
  string,
  Array<"accounts" | "currencies" | null>
> = {
  open: ["accounts", "currencies"],
  close: ["accounts"],
  commodity: ["currencies"],
  balance: ["accounts", null, "currencies"],
  pad: ["accounts", "accounts"],
  note: ["accounts"],
  document: ["accounts"],
  price: ["currencies", null, "currencies"],
};

  const doc = cm.getDoc();
  const cursor = doc.getCursor();
  const line = doc.getLine(cursor.line);
  const token = cm.getTokenAt(cursor);

  const lineTokens = cm.getLineTokens(cursor.line);

  if (lineTokens.length > 0) {
    const startCurrentWord = cursor.ch - currentWord.length;
    const previousTokens = lineTokens.filter((d) => d.end <= startCurrentWord);

    // dated directives
    if (lineTokens[0].type === "date") {

      // Ignore negative sign from previousTokens
      const tokenLength = previousTokens.filter((t) => t.type != null).length;
      if (tokenLength % 2 === 0) {
        const directiveType = previousTokens[2].string;
        if (directiveType in directiveCompletions) {
          const complType =
            directiveCompletions[directiveType][tokenLength / 2 - 2];
          if (complType) {
            return fuzzyMatch(cursor, currentWord, getCompletion(complType));
          }
        }
      }
    }
  }

  return {
    list: [],
  };
});
*/
