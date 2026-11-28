import { ensureSyntaxTree } from "@codemirror/language";
import type { EditorState } from "@codemirror/state";
import { group } from "d3-array";

import {
  type EditableEntry,
  EntryMetadata,
  Posting,
  Transaction,
} from "../entries/index.ts";
import { get_ts_tree } from "./tree-sitter-parser.ts";

/** Duplicate the saved entry with posting amounts as written before booking. */
export function duplicate_entry(
  entry: EditableEntry,
  date: string,
  source: EditorState,
): EditableEntry {
  const copy = entry.set("date", date);
  if (!(copy instanceof Transaction)) {
    return copy;
  }
  const tree = ensureSyntaxTree(source, source.doc.length);
  const parsed = tree && get_ts_tree(tree);
  if (!parsed || parsed.rootNode.hasError) {
    return copy;
  }

  // Booking can reorder postings or split one source line across currencies or lots.
  const booked = group(copy.postings, (posting) => Number(posting.meta.lineno));
  const postings: Posting[] = [];
  for (const node of parsed.rootNode.descendantsOfType("posting")) {
    const account = node.childForFieldName("account")?.text;
    if (account == null) {
      return copy;
    }
    const line = Number(entry.meta.lineno) + node.startPosition.row;
    const matches = booked.get(line) ?? [];
    const original_meta = matches[0]?.meta;
    // An automatic posting can disappear if the other postings already balance.
    if (!original_meta && node.childForFieldName("metadata")) {
      return copy;
    }
    const meta = original_meta ?? new EntryMetadata();
    if (
      matches.some(
        (p) =>
          p.account !== account ||
          p.meta.filename !== entry.meta.filename ||
          (p.meta !== meta &&
            JSON.stringify(p.meta.entries()) !==
              JSON.stringify(meta.entries())),
      )
    ) {
      return copy;
    }
    const amount = ["amount", "cost_spec", "price_annotation"]
      .map((field) => node.childForFieldName(field)?.text)
      .filter(Boolean)
      .join(" ");
    postings.push(new Posting(meta, account, amount));
    booked.delete(line);
  }
  // Keep the booked entry if a plugin added postings with no matching source.
  return booked.size ? copy : copy.set("postings", postings);
}
