import type {
  Completion,
  CompletionContext,
  CompletionResult,
  CompletionSource,
} from "@codemirror/autocomplete";
import { syntaxTree } from "@codemirror/language";
import { get as store_get } from "svelte/store";

import { escape_for_regex } from "../lib/regex.ts";
import { payees } from "../stores/index.ts";
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

const payee_completions = (
  values: readonly string[],
  quote: string,
  regexp: boolean,
): Completion[] =>
  values
    // Inserting the active delimiter would terminate the BQL string.
    .filter((label) => !label.includes(quote))
    .map((label) => ({
      label,
      apply: regexp ? escape_for_regex(label) : label,
    }));

/** Complete BQL syntax and payee string values. */
export function complete_bql(
  context: CompletionContext,
  payee_values: readonly string[],
): CompletionResult | null {
  const string_node = syntaxTree(context.state).resolveInner(context.pos, -1);
  const payee_node = string_node.prevSibling;
  const quote = context.state.sliceDoc(string_node.from, string_node.from + 1);
  const operator = payee_node
    ? /^\s*(!?=|!?~)\s*$/.exec(
        context.state.sliceDoc(payee_node.to, string_node.from),
      )?.[1]
    : undefined;
  if (
    string_node.name === "string" &&
    context.pos > string_node.from &&
    context.pos < string_node.to &&
    (quote === '"' || quote === "'") &&
    context.state.sliceDoc(string_node.to - 1, string_node.to) === quote &&
    payee_node?.name === "typeName" &&
    context.state.sliceDoc(payee_node.from, payee_node.to).toLowerCase() ===
      "payee" &&
    operator !== undefined
  ) {
    return {
      from: string_node.from + 1,
      to: string_node.to - 1,
      options: payee_completions(payee_values, quote, operator.endsWith("~")),
      validFor: quote === '"' ? /^[^"]*$/ : /^[^']*$/,
    };
  }

  const token = context.matchBefore(/\w+/);
  if (!token) {
    return null;
  }
  if (token.from === 0) {
    return { from: token.from, options: command_completions };
  }
  return { from: token.from, options: columns_functions_keywords };
}

export const bql_completion: CompletionSource = (context) =>
  complete_bql(context, store_get(payees));
