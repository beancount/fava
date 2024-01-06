/**
 * Use a tree-sitter parser to generate Lezer parse tree.s
 *
 * To be able to reuse the existing tree-sitter grammar and parser for the Fava editor,
 * this module provides functionality to translate between a tree-sitter parse tree and
 * a Lezer one.
 */

import { DocInput } from "@codemirror/language";
import type { Text } from "@codemirror/state";
import type {
  Input,
  NodePropSource,
  PartialParse,
  TreeFragment,
} from "@lezer/common";
import { NodeProp, NodeType, Parser, Tree } from "@lezer/common";
import { styleTags, tags } from "@lezer/highlight";
import type TSParser from "web-tree-sitter";

import type { NonEmptyArray } from "../lib/array";
import { is_non_empty, last_element } from "../lib/array";
import { assert, log_error } from "../log";

/** The Lezer NodeType for error nodes. */
const error = NodeType.define({
  id: 65535,
  name: "ERROR",
  error: true,
  props: [styleTags({ ERROR: tags.invalid })],
});

// Since we need to pass points (row, column) to some tree-sitter APIs but
// we usually do not have this information, pass this dummy point. Should work
// as long as we do not use any of the APIs returning points:
// https://github.com/tree-sitter/tree-sitter/issues/445
const dummyPosition: TSParser.Point = { row: 0, column: 0 };

/** Get a TS edit for the three byte offsets with dummy row/column-offsets. */
function ts_edit(
  startIndex: number,
  oldEndIndex: number,
  newEndIndex: number,
): TSParser.Edit {
  return {
    startIndex,
    oldEndIndex,
    newEndIndex,
    startPosition: dummyPosition,
    oldEndPosition: dummyPosition,
    newEndPosition: dummyPosition,
  };
}

/** This node prop is used to store the TS tree on the root node of the Lezer tree for reuse. */
const TSTreeProp = new NodeProp<TSParser.Tree>({ perNode: true });

class TSParserError extends Error {}

class InvalidRangeError extends TSParserError {
  constructor() {
    super("Only one range spanning the whole document is supported.");
  }
}

/** Information about a change between an old parse and a new one. */
interface ChangeDetails {
  /** The edit (to simplify things, we reduce it to a single change) */
  edit: TSParser.Edit;
  /** The old Lezer syntax tree (not adjusted for edit). */
  old_tree: Tree;
  /** The TS tree, adjusted for the edit - is used to extend the edit for safe reuse of the Lezer tree. */
  edited_old_ts_tree: TSParser.Tree;
}

/** Deduce a TSParser.Edit from the given Lezer TreeFragments. */
export function input_edit_for_fragments(
  fragments: NonEmptyArray<TreeFragment>,
  input_length: number,
): TSParser.Edit | null {
  const [fragment] = fragments;
  const { tree } = fragment;

  if (!fragments.every((f) => f.tree === tree)) {
    log_error("expect fragments to all have the same tree", fragments);
    return null;
  }

  if (fragments.length === 1) {
    return fragment.offset === 0
      ? ts_edit(fragment.to - 1, tree.length, input_length)
      : ts_edit(0, fragment.from + fragment.offset + 1, fragment.from + 1);
  }

  const before =
    [...fragments].reverse().find((f) => !f.openStart && f.openEnd) ?? fragment;
  const after =
    fragments.find((f) => f.openStart && !f.openEnd) ?? last_element(fragments);

  const from = before.to;
  const { offset } = after;
  const newEndIndex = after.from;
  const oldEndIndex = newEndIndex + offset;

  return ts_edit(from - 1, oldEndIndex + 1, newEndIndex + 1);
}

/**
 * A parse can to be started for the same document multiple times.
 *
 * Since we only do full parses, we can reuse these trees here.
 */
const PARSE_CACHE = new WeakMap<Text, Tree>();

/**
 * This does not support any partial parsing since tree-sitter does not either.
 *
 * It tries to reuse any existing trees (as passed indirectly via fragments) to
 * allow for a faster incremental parse.
 */
class Parse implements PartialParse {
  stoppedAt: number | null = null;

  parsedPos = 0;

  constructor(
    readonly ts_parser: TSParser,
    readonly node_types: NodeType[],
    readonly input: Input,
    readonly fragments: readonly TreeFragment[],
    readonly ranges: readonly { from: number; to: number }[],
  ) {
    if (
      ranges.length !== 1 ||
      ranges[0]?.from !== 0 ||
      ranges[0]?.to !== input.length
    ) {
      throw new InvalidRangeError();
    }
  }

  /** Walk over the given node and its children, recursively creating Trees. */
  private get_tree_for_ts_cursor(ts_cursor: TSParser.TreeCursor): Tree {
    const { nodeTypeId, startIndex, endIndex } = ts_cursor;
    const node_type = this.node_types[nodeTypeId] ?? error;
    const children: Tree[] = [];
    const positions: number[] = [];

    if (ts_cursor.gotoFirstChild()) {
      do {
        positions.push(ts_cursor.startIndex - startIndex);
        children.push(this.get_tree_for_ts_cursor(ts_cursor));
      } while (ts_cursor.gotoNextSibling());
      ts_cursor.gotoParent();
    }

    return new Tree(node_type, children, positions, endIndex - startIndex);
  }

  /**
   * Walk over the given node and its children, recursively creating Trees.
   *
   * Tries to reuse parts of an old tree.
   */
  private get_tree_for_ts_cursor_reuse(
    ts_cursor: TSParser.TreeCursor,
    edit: TSParser.Edit,
    old_tree: Tree,
  ): Tree {
    const { nodeTypeId, startIndex, endIndex } = ts_cursor;
    const node_type = this.node_types[nodeTypeId] ?? error;
    const children: Tree[] = [];
    const positions: number[] = [];

    if (ts_cursor.gotoFirstChild()) {
      let ended = false;
      const old_children = old_tree.children;

      // First, we add all children that end before the edit.
      let child_index = 0;
      while (!ended && ts_cursor.endIndex < edit.startIndex) {
        positions.push(ts_cursor.startIndex - startIndex);
        children.push(old_children[child_index] as Tree);
        child_index += 1;
        ended = !ts_cursor.gotoNextSibling();
      }

      // If there is a node that completely covers the edit, we want to pass
      // the old tree for the node down so that parts can be reused.
      if (
        ts_cursor.startIndex < edit.startIndex &&
        edit.newEndIndex < ts_cursor.endIndex
      ) {
        const old_child = old_children[child_index] as Tree | undefined;
        if (old_child) {
          positions.push(ts_cursor.startIndex - startIndex);
          children.push(
            this.get_tree_for_ts_cursor_reuse(ts_cursor, edit, old_child),
          );
          ended = !ts_cursor.gotoNextSibling();
        }
      }

      // Now/alternatively, we add all children contained in/touching the edit.
      while (!ended && ts_cursor.startIndex < edit.newEndIndex) {
        positions.push(ts_cursor.startIndex - startIndex);
        children.push(this.get_tree_for_ts_cursor(ts_cursor));
        ended = !ts_cursor.gotoNextSibling();
      }

      // Finally, we add the children after the edit.
      // We first count them and add their positions and push the trees after that.
      let children_after_edit = 0;
      while (!ended) {
        positions.push(ts_cursor.startIndex - startIndex);
        children_after_edit += 1;
        ended = !ts_cursor.gotoNextSibling();
      }
      if (children_after_edit > 0) {
        children.push(...(old_children.slice(-children_after_edit) as Tree[]));
      }
      ts_cursor.gotoParent();
    }

    return new Tree(node_type, children, positions, endIndex - startIndex);
  }

  /** Convert the tree-sitter Tree to a Lezer tree, possibly reusing parts of an old one. */
  private convert_tree(
    ts_tree: TSParser.Tree,
    change: Pick<ChangeDetails, "edit" | "old_tree"> | null,
  ): Tree {
    const ts_tree_cursor = ts_tree.rootNode.walk();
    const tree = change
      ? this.get_tree_for_ts_cursor_reuse(
          ts_tree_cursor,
          change.edit,
          change.old_tree,
        )
      : this.get_tree_for_ts_cursor(ts_tree_cursor);
    const tree_with_ts_tree_prop = new Tree(
      tree.type,
      tree.children,
      tree.positions,
      tree.length,
      [[TSTreeProp, ts_tree]],
    );
    return tree_with_ts_tree_prop;
  }

  /** Gather information about the changes from a previous parse. */
  private static change_details(
    fragments: readonly TreeFragment[],
    input_length: number,
  ): ChangeDetails | null {
    if (!is_non_empty(fragments)) {
      return null;
    }
    const edit = input_edit_for_fragments(fragments, input_length);
    const old_tree = fragments[0].tree;
    const edited_old_ts_tree = old_tree.prop(TSTreeProp)?.copy();

    if (edit) {
      if (!edited_old_ts_tree) {
        log_error("expected old tree when there is an edit");
        return null;
      }
      assert(
        input_length - old_tree.length === edit.newEndIndex - edit.oldEndIndex,
        "expect offset to match change in text length",
      );
      edited_old_ts_tree.edit(edit); // unlike the types suggest this does modify in-place
      assert(
        edited_old_ts_tree.rootNode.endIndex === input_length,
        "expect edited old tree to match text length",
      );
      return { edit, old_tree, edited_old_ts_tree };
    }

    return null;
  }

  /**
   * Extend the changed range using the TS getChangedRanges function.
   *
   * Outside this extended range, nodes from the old tree can be reused since they
   * will have the exact same stack of containing nodes (possibly offset after the edit).
   */
  private static extend_change(
    change: ChangeDetails,
    ts_tree: TSParser.Tree,
  ): Pick<ChangeDetails, "edit" | "old_tree"> | null {
    const { edit, edited_old_ts_tree } = change;
    const changed_ranges = edited_old_ts_tree.getChangedRanges(ts_tree);
    if (!is_non_empty(changed_ranges)) {
      return change;
    }
    const newEndIndex = Math.max(
      edit.newEndIndex,
      last_element(changed_ranges).endIndex,
    );
    const extended_edit = ts_edit(
      Math.min(edit.startIndex, changed_ranges[0].startIndex),
      newEndIndex + (edit.oldEndIndex - edit.newEndIndex),
      newEndIndex,
    );
    return {
      edit: extended_edit,
      old_tree: change.old_tree,
    };
  }

  advance(): Tree | null {
    const { fragments, input, stoppedAt, ts_parser } = this;
    const text = input.read(0, stoppedAt ?? input.length);
    const input_length = text.length;

    const cm_text = input instanceof DocInput ? input.doc : null;
    if (cm_text) {
      const cached = PARSE_CACHE.get(cm_text);
      if (cached) {
        return cached;
      }
    }

    const change = Parse.change_details(fragments, input_length);
    let ts_tree = ts_parser.parse(text, change?.edited_old_ts_tree);
    if (ts_tree.rootNode.endIndex !== input_length) {
      log_error(
        "Mismatch between tree (%s) and document (%s) lengths; reparsing",
        ts_tree.rootNode.endIndex,
        input_length,
      );
      ts_tree = ts_parser.parse(text);
    }
    const extended_change = change
      ? Parse.extend_change(change, ts_tree)
      : null;

    // Convert the Lezer tree to a tree-sitter tree.
    const tree = this.convert_tree(ts_tree, extended_change);
    this.parsedPos = input_length;
    if (cm_text) {
      PARSE_CACHE.set(cm_text, tree);
    }

    return tree;
  }

  stopAt(pos: number): void {
    this.stoppedAt = pos;
  }
}

/**
 * A parser using a tree-sitter parser to create Lezer trees.
 *
 * @param ts_parser - The tree-sitter parser (with a language loaded) to use.
 * @param props - Node props to assign to the node types.
 * @param top_node - The name of the node type that is the top node in the TS grammar.
 */
export class LezerTSParser extends Parser {
  /** The Lezer NodeTypes - all node types from the TS grammar with props assigned. */
  private node_types: NodeType[];

  constructor(
    readonly ts_parser: TSParser,
    props: NodePropSource[],
    top_node: string,
  ) {
    super();

    // @ts-expect-error Type definitions seem to be incomplete and missing this attribute.
    const types = ts_parser.getLanguage().types as string[];
    this.node_types = types.map((name, id) =>
      NodeType.define({ id, name, props, top: name === top_node }),
    );
  }

  createParse(
    input: Input,
    fragments: readonly TreeFragment[],
    ranges: readonly { from: number; to: number }[],
  ): PartialParse {
    return new Parse(this.ts_parser, this.node_types, input, fragments, ranges);
  }
}
