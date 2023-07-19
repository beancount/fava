/**
 * Use a tree-sitter parser to generate Lezer parse tree.s
 *
 * To be able to reuse the existing tree-sitter grammar and parser for the Fava editor,
 * this module provides functionality to translate between a tree-sitter parse tree and
 * a Lezer one.
 */

import type {
  Input,
  NodePropSource,
  PartialParse,
  TreeCursor,
  TreeFragment,
} from "@lezer/common";
import { NodeProp, NodeType, Parser, Tree } from "@lezer/common";
import type TSParser from "web-tree-sitter";

/** The Lezer NodeType for error nodes. */
const error = NodeType.define({ id: 65535, name: "ERROR", error: true });

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

interface ChangeDetails {
  edit: TSParser.Edit;
  old_tree: Tree;
  edited_old_ts_tree: TSParser.Tree;
}

/**
 * This does not support any partial parsing since tree-sitter does not either.
 *
 * It tries to reuse any existing trees (as passed indirectly via fragments) to
 * allow for a faster incremental parse.
 */
class Parse implements PartialParse {
  // TODO: handle stopped parse
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
  private get_tree_for_ts_cursor(
    ts_cursor: TSParser.TreeCursor,
    edit?: TSParser.Edit,
    old_cursor?: TreeCursor,
  ): Tree {
    const { nodeTypeId, startIndex, endIndex } = ts_cursor;
    if (edit && endIndex < edit.startIndex && old_cursor?.tree) {
      // This is before any changed range (as determined by TS), so just reuse the tree.
      return old_cursor.tree;
    }
    const node_type = this.node_types[nodeTypeId] ?? error;
    const trees: Tree[] = [];
    const positions: number[] = [];

    if (ts_cursor.gotoFirstChild()) {
      old_cursor?.firstChild();
      do {
        positions.push(ts_cursor.startIndex - startIndex);
        trees.push(this.get_tree_for_ts_cursor(ts_cursor, edit, old_cursor));
        old_cursor?.nextSibling();
      } while (ts_cursor.gotoNextSibling());
      ts_cursor.gotoParent();
      old_cursor?.parent();
    }

    return new Tree(node_type, trees, positions, endIndex - startIndex);
  }

  /** Convert the tree-sitter Tree to a Lezer tree, possibly reusing parts of an old one. */
  private convert_tree(
    ts_tree: TSParser.Tree,
    change: ChangeDetails | null,
  ): Tree {
    const tree = this.get_tree_for_ts_cursor(
      ts_tree.rootNode.walk(),
      change?.edit,
      change?.old_tree.cursor(),
    );
    const tree_with_ts_tree_prop = new Tree(
      tree.type,
      tree.children,
      tree.positions,
      tree.length,
      [[TSTreeProp, ts_tree]],
    );
    return tree_with_ts_tree_prop;
  }

  /** Deduce a TSParser.Edit from the given Lezer TreeFragments. */
  input_edit_for_fragments(): TSParser.Edit | null {
    const [left, right] = this.fragments;
    // for the very common case of having exactly two tree fragments, one at the start
    // of the document up to the change and one after it to the end of the document,
    // we produce a tree-sitter edit to reuse the old tree-sitter tree.
    if (
      left?.from === 0 &&
      right?.to === this.input.length &&
      this.fragments.length === 2
    ) {
      return ts_edit(left.to, right.from, right.from - right.offset);
    }
    return null;
  }

  /** Gather information about the changes from a previous parse. */
  private change_details(): ChangeDetails | null {
    const edit = this.input_edit_for_fragments();
    const old_tree = this.fragments[0]?.tree;
    const edited_old_ts_tree = old_tree?.prop(TSTreeProp)?.copy();

    if (!edit || !old_tree || !edited_old_ts_tree) {
      return null;
    }
    edited_old_ts_tree.edit(edit); // unlike the types suggest this does modify in-place
    if (edited_old_ts_tree.rootNode.endIndex !== this.input.length) {
      // This seems to happen sometimes - usually only on some deletion. The reason is unclear
      // but let's just do a full reparse in this case.
      // eslint-disable-next-line no-console
      console.error(
        "Unexpected tree length after edit - do a full parse",
        edit,
        edited_old_ts_tree.rootNode.endIndex,
        this.input.length,
      );
      return null;
    }

    return { edit, old_tree, edited_old_ts_tree };
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
  ): ChangeDetails {
    const { edit, edited_old_ts_tree } = change;
    const changed_ranges = edited_old_ts_tree.getChangedRanges(ts_tree);
    const newEndIndex =
      changed_ranges[changed_ranges.length - 1]?.endIndex ?? edit.newEndIndex;
    const extended_edit = ts_edit(
      changed_ranges[0]?.startIndex ?? edit.startIndex,
      newEndIndex + (edit.oldEndIndex - edit.newEndIndex),
      newEndIndex,
    );
    return {
      ...change,
      edit: extended_edit,
    };
  }

  advance(): Tree | null {
    const { input } = this;
    const parseEnd = this.stoppedAt ?? input.length;

    const text = this.input.read(0, parseEnd);
    const change = this.change_details();
    const ts_tree = this.ts_parser.parse(text, change?.edited_old_ts_tree);
    const extended_change = change
      ? Parse.extend_change(change, ts_tree)
      : null;

    // Convert the Lezer tree to a tree-sitter tree.
    const tree = this.convert_tree(ts_tree, extended_change);
    this.parsedPos = parseEnd;

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
