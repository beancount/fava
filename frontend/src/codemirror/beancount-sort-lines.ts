import type { ChangeSpec, EditorState } from "@codemirror/state";
import type { Command } from "@codemirror/view";

/**
 * Line ranges the sort command applies to: one per non-empty selection,
 * or the whole document (excluding a trailing empty line after a final newline).
 */
function line_blocks(state: EditorState): Array<{ from: number; to: number }> {
  const ranges = state.selection.ranges.filter((r) => !r.empty);
  if (!ranges.length) {
    const { doc } = state;
    const last = doc.line(doc.lines);
    return [
      {
        from: 0,
        to:
          !last.length && doc.lines > 1
            ? doc.line(doc.lines - 1).to
            : doc.length,
      },
    ];
  }
  const blocks: Array<{ from: number; to: number }> = [];
  for (const range of ranges) {
    const first = state.doc.lineAt(range.from);
    // A selection ending at a line start does not include that line.
    const last = state.doc.lineAt(
      range.to > range.from && state.doc.lineAt(range.to).from === range.to
        ? range.to - 1
        : range.to,
    );
    const prev = blocks[blocks.length - 1];
    if (prev && first.from <= prev.to) {
      prev.to = Math.max(prev.to, last.to);
    } else {
      blocks.push({ from: first.from, to: last.to });
    }
  }
  return blocks;
}

/** Build document changes to sort selected (or all) lines. */
export function sort_lines_changes(
  state: EditorState,
  descending: boolean,
): ChangeSpec[] {
  const collator = new Intl.Collator(undefined, { sensitivity: "variant" });
  const changes: ChangeSpec[] = [];
  for (const block of line_blocks(state)) {
    const text = state.sliceDoc(block.from, block.to);
    const lines = text.split(state.lineBreak);
    if (lines.length < 2) {
      continue;
    }
    const sorted = [...lines].sort((a, b) =>
      descending ? collator.compare(b, a) : collator.compare(a, b),
    );
    const next = sorted.join(state.lineBreak);
    if (next !== text) {
      changes.push({ from: block.from, to: block.to, insert: next });
    }
  }
  return changes;
}

function make_sort_command(descending: boolean): Command {
  return (view) => {
    const changes = sort_lines_changes(view.state, descending);
    if (changes.length) {
      view.dispatch({
        changes,
        userEvent: descending ? "input.sort.desc" : "input.sort.asc",
      });
    }
    return true;
  };
}

/** Sort selected lines (or the whole document) ascending. */
export const sort_lines_ascending = make_sort_command(false);

/** Sort selected lines (or the whole document) descending. */
export const sort_lines_descending = make_sort_command(true);
