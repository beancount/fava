import type { CompletionSource } from "@codemirror/autocomplete";

import bql_grammar from "./bql-grammar.ts";

const { columns, functions, keywords } = bql_grammar;

const columns_functions_keywords = [
  ...columns,
  ...functions.map((f) => `${f}(`),
  ...keywords,
].map((label) => ({ label }));

const command_completions = [
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
].map((label) => ({ label }));

export const bql_completion: CompletionSource = (context) => {
  const token = context.matchBefore(/\w+/);
  if (!token) {
    return null;
  }
  if (token.from === 0) {
    return { from: token.from, options: command_completions };
  }
  return { from: token.from, options: columns_functions_keywords };
};
