import type { CompletionSource } from "@codemirror/autocomplete";

import bqlGrammar from "./bql-grammar";

const { columns, functions, keywords } = bqlGrammar;

const completions = [...columns, ...functions.map((f) => `${f}(`), ...keywords];
const allCompletionOptions = completions.map((label) => ({ label }));

const commands = [
  "balances",
  "errors",
  "explain",
  "help",
  "lex",
  "parse",
  "print",
  "runcustom",
  "select",
  "tokenize",
];
const firstWordCompletions = commands.map((label) => ({ label }));

export const bqlCompletion: CompletionSource = (context) => {
  const token = context.matchBefore(/\w+/);
  if (!token) {
    return null;
  }
  if (token.from === 0) {
    return { from: token.from, options: firstWordCompletions };
  }
  return { from: token.from, options: allCompletionOptions };
};
