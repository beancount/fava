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

const directiveCompletions: Record<
  string,
  Array<"accounts" | "currencies" | null> | undefined
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

export const beancountCompletion: CompletionSource = (context) => {
  const { state, pos } = context;
  const { doc } = state;

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

  const line = doc.lineAt(pos);
  const currentWord = context.matchBefore(/\S*/);
  if (currentWord?.from === line.from && line.length > 0) {
    return { options: opts(undatedDirectives), from: line.from };
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
    // Dates have the 'number.special' token name
    if (first.name === "number.special" && line.length > last.to) {
      if (tokens.length === 1) {
        return {
          options: opts(datedDirectives),
          from: line.from + first.to + 1,
        };
      }
      const directive = lineContent.slice(tokens[1].from, tokens[1].to);
      const compl = directiveCompletions[directive];
      if (compl) {
        const complType = compl[tokens.length - 2];
        if (complType) {
          return {
            options: opts(getCompletion(complType)),
            from: line.from + last.to + 1,
          };
        }
      }
    }
  }

  return null;
};
