import { ensureSyntaxTree } from "@codemirror/language";
import type { ChangeSpec } from "@codemirror/state";
import type { Command } from "@codemirror/view";
import { get as store_get } from "svelte/store";
import type { Tree as TSTree } from "web-tree-sitter";
import { Query } from "web-tree-sitter";

import { notify } from "../notifications.ts";
import { currency_column } from "../stores/fava_options.ts";
import { get_ts_tree } from "./tree-sitter-parser.ts";

/** The amounts to align - not the ones in e.g. costs or custom directives. */
const AMOUNTS_QUERY = `
(posting (amount) @amount)
(balance [(amount) (amount_with_tolerance)] @amount)
(price (amount) @amount)
(metadata (key_value (amount) @amount))
`;

/**
 * Get the changes to align the currencies of amounts at the given column.
 *
 * There are at least two spaces before the number (or number with tolerance)
 * and a single one before the currency. Amounts that span multiple lines or
 * whose parent node contains a syntax error are left alone.
 */
export function align_amounts(
  text: string,
  tree: TSTree,
  column: number,
): ChangeSpec[] {
  const changes: ChangeSpec[] = [];
  const query = new Query(tree.language, AMOUNTS_QUERY);
  try {
    for (const { node } of query.captures(tree.rootNode)) {
      const from = node.startIndex;
      const currency = node.lastChild;
      const number_end = currency?.previousSibling?.endIndex;
      if (
        currency?.type !== "currency" ||
        number_end == null ||
        node.parent?.hasError !== false ||
        text.slice(from, currency.startIndex).includes("\n")
      ) {
        continue;
      }
      const line_start = text.lastIndexOf("\n", from - 1) + 1;
      const prefix_end =
        line_start + text.slice(line_start, from).trimEnd().length;
      const spaces = Math.max(
        2,
        column - 2 - (prefix_end - line_start) - (number_end - from),
      );
      for (const change of [
        { from: prefix_end, to: from, insert: " ".repeat(spaces) },
        { from: number_end, to: currency.startIndex, insert: " " },
      ]) {
        if (text.slice(change.from, change.to) !== change.insert) {
          changes.push(change);
        }
      }
    }
  } finally {
    query.delete();
  }
  return changes;
}

/** Align currencies in one column. */
export const beancount_format: Command = (cm) => {
  const { state } = cm;
  const tree = ensureSyntaxTree(state, state.doc.length, 5000);
  const ts_tree = tree && get_ts_tree(tree);
  if (!ts_tree) {
    notify("Formatting source failed: could not parse the file.", "error");
    return true;
  }
  const column = store_get(currency_column);
  const changes = align_amounts(state.sliceDoc(), ts_tree, column);
  if (changes.length) {
    cm.dispatch({ changes, userEvent: "input.format" });
  }
  return true;
};
