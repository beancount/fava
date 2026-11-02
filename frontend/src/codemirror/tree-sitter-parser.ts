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
import type {
  Parser as TSParser,
  Tree as TSTree,
  TreeCursor as TSTreeCursor,
} from "web-tree-sitter";
import { Edit as TSEdit } from "web-tree-sitter";

import type { NonEmptyArray } from "../lib/array.ts";
import { is_non_empty, last_element } from "../lib/array.ts";
import { assert, log_error } from "../log.ts";

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
const dummyPosition = Object.freeze({ row: 0, column: 0 });

/** Get a TS edit for the three byte offsets with dummy row/column-offsets. */
function ts_edit(
  startIndex: number,
  oldEndIndex: number,
  newEndIndex: number,
): TSEdit {
  return new TSEdit({
    startIndex,
    oldEndIndex,
    newEndIndex,
    startPosition: dummyPosition,
    oldEndPosition: dummyPosition,
    newEndPosition: dummyPosition,
  });
}

/** This node prop is used to store the TS tree on the root node of the Lezer tree for reuse. */
const TS_TREE_PROP = new NodeProp<TSTree>({ perNode: true });

class TSParserError extends Error {}

class InvalidRangeError extends TSParserError {
  constructor() {
    super("Only one range spanning the whole document is supported.");
  }
}

class MissingLanguageError extends TSParserError {
  constructor() {
    super("Parser is missing language.");
  }
}

/** Information about a change between an old parse and a new one. */
interface ChangeDetails {
  /** The edit (to simplify things, we reduce it to a single change) */
  edit: TSEdit;
  /** The old Lezer syntax tree (not adjusted for edit). */
  old_tree: Tree;
  /** The TS tree, adjusted for the edit - is used to extend the edit for safe reuse of the Lezer tree. */
  edited_old_ts_tree: TSTree;
}

/** Deduce a TSParser.Edit from the given Lezer TreeFragments. */
export function input_edit_for_fragments(
  fragments: NonEmptyArray<TreeFragment>,
  input_length: number,
): TSEdit | null {
  const [fragment] = fragments;
  const { tree } = fragment;

  if (!fragments.every((f) => f.tree === tree)) {
    log_error("expect fragments to all have the same tree", fragments);
    return null;
  }

  // The edit spans from the first to the last change, so it starts at the
  // beginning (or ends at the end) unless a fragment is unchanged there.
  const last = last_element(fragments);
  const from = fragment.openStart ? 0 : fragment.to - 1;
  return last.openEnd || !last.openStart
    ? ts_edit(from, tree.length, input_length)
    : ts_edit(from, last.from + last.offset + 1, last.from + 1);
}

/**
 * This does not support any partial parsing since tree-sitter does not either.
 *
 * It tries to reuse any existing trees (as passed indirectly via fragments) to
 * allow for a faster incremental parse.
 */
class Parse implements PartialParse {
  readonly ts_parser: TSParser;
  readonly node_types: NodeType[];
  readonly cache: WeakMap<Text, Tree>;
  readonly input: Input;
  readonly fragments: readonly TreeFragment[];
  readonly ranges: readonly { from: number; to: number }[];
  stoppedAt: number | null = null;
  parsedPos = 0;

  constructor(
    ts_parser: TSParser,
    node_types: NodeType[],
    cache: WeakMap<Text, Tree>,
    input: Input,
    fragments: readonly TreeFragment[],
    ranges: readonly { from: number; to: number }[],
  ) {
    this.ts_parser = ts_parser;
    this.node_types = node_types;
    this.cache = cache;
    this.input = input;
    this.fragments = fragments;
    this.ranges = ranges;
    if (
      ranges.length !== 1 ||
      ranges[0]?.from !== 0 ||
      ranges[0].to !== input.length
    ) {
      throw new InvalidRangeError();
    }
  }

  /** Walk over the given node and its children, recursively creating Trees. */
  #get_tree_for_ts_cursor(ts_cursor: TSTreeCursor): Tree {
    const { startIndex, endIndex } = ts_cursor;
    const children: Tree[] = [];
    const positions: number[] = [];

    if (ts_cursor.gotoFirstChild()) {
      do {
        positions.push(ts_cursor.startIndex - startIndex);
        children.push(this.#get_tree_for_ts_cursor(ts_cursor));
      } while (ts_cursor.gotoNextSibling());
      ts_cursor.gotoParent();
    }

    return new Tree(
      this.node_types[ts_cursor.nodeTypeId] ?? error,
      children,
      positions,
      endIndex - startIndex,
    );
  }

  /**
   * Walk over the given node and its children, recursively creating Trees.
   *
   * Tries to reuse parts of an old tree.
   */
  #get_tree_for_ts_cursor_reuse(
    ts_cursor: TSTreeCursor,
    edit: TSEdit,
    old_tree: Tree,
  ): Tree {
    const { startIndex, endIndex } = ts_cursor;
    const children: Tree[] = [];
    const positions: number[] = [];

    if (ts_cursor.gotoFirstChild()) {
      let ended = false;
      const old_children = old_tree.children;

      // First, we add all children that end before the edit.
      // Here and after the edit, if an old child does not match, we fall back
      // to converting the node.
      let child_index = 0;
      while (!ended && ts_cursor.endIndex < edit.startIndex) {
        const old_child = old_children[child_index];
        if (
          !(old_child instanceof Tree) ||
          old_child.type.id !== ts_cursor.nodeTypeId ||
          old_child.length !== ts_cursor.endIndex - ts_cursor.startIndex
        ) {
          ts_cursor.gotoParent();
          return this.#get_tree_for_ts_cursor(ts_cursor);
        }
        positions.push(ts_cursor.startIndex - startIndex);
        children.push(old_child);
        child_index += 1;
        ended = !ts_cursor.gotoNextSibling();
      }

      // If there is a node that completely covers the edit, we want to pass
      // the old tree for the node down so that parts can be reused.
      if (
        ts_cursor.startIndex < edit.startIndex &&
        edit.newEndIndex < ts_cursor.endIndex
      ) {
        const old_child = old_children[child_index];
        if (
          old_child instanceof Tree &&
          old_child.type.id === ts_cursor.nodeTypeId
        ) {
          positions.push(ts_cursor.startIndex - startIndex);
          children.push(
            this.#get_tree_for_ts_cursor_reuse(ts_cursor, edit, old_child),
          );
          ended = !ts_cursor.gotoNextSibling();
        }
      }

      // Now/alternatively, we add all children contained in/touching the edit.
      while (!ended && ts_cursor.startIndex < edit.newEndIndex) {
        positions.push(ts_cursor.startIndex - startIndex);
        children.push(this.#get_tree_for_ts_cursor(ts_cursor));
        ended = !ts_cursor.gotoNextSibling();
      }

      // Finally, we add the children after the edit.
      // We first count them and add their positions and push the trees after that.
      const after: [number, number][] = [];
      while (!ended) {
        positions.push(ts_cursor.startIndex - startIndex);
        after.push([
          ts_cursor.nodeTypeId,
          ts_cursor.endIndex - ts_cursor.startIndex,
        ]);
        ended = !ts_cursor.gotoNextSibling();
      }
      const reused = old_children.slice(old_children.length - after.length);
      if (
        reused.length !== after.length ||
        !reused.every(
          (t, i): t is Tree =>
            t instanceof Tree &&
            t.type.id === after[i]?.[0] &&
            t.length === after[i][1],
        )
      ) {
        ts_cursor.gotoParent();
        return this.#get_tree_for_ts_cursor(ts_cursor);
      }
      children.push(...reused);
      ts_cursor.gotoParent();
    }

    return new Tree(
      this.node_types[ts_cursor.nodeTypeId] ?? error,
      children,
      positions,
      endIndex - startIndex,
    );
  }

  /** Convert the tree-sitter Tree to a Lezer tree, possibly reusing parts of an old one. */
  #convert_tree(
    ts_tree: TSTree,
    change: Pick<ChangeDetails, "edit" | "old_tree"> | null,
  ): Tree {
    const root_node = ts_tree.rootNode;
    const ts_tree_cursor = root_node.walk();
    let tree: Tree;
    try {
      tree = change
        ? this.#get_tree_for_ts_cursor_reuse(
            ts_tree_cursor,
            change.edit,
            change.old_tree,
          )
        : this.#get_tree_for_ts_cursor(ts_tree_cursor);
    } finally {
      // Delete explicitly: the finalizer of web-tree-sitter (0.27.1) does not
      // restore the cursor state before deleting it, corrupting other cursors.
      ts_tree_cursor.delete();
    }
    const { startIndex: start_index, endIndex: end_index } = root_node;
    const tree_with_ts_tree_prop = new Tree(
      tree.type,
      tree.children,
      tree.positions.map((pos) => pos + start_index),
      end_index,
      [[TS_TREE_PROP, ts_tree]],
    );
    return tree_with_ts_tree_prop;
  }

  /** Gather information about the changes from a previous parse. */
  static #change_details(
    fragments: readonly TreeFragment[],
    input_length: number,
  ): ChangeDetails | null {
    if (!is_non_empty(fragments)) {
      return null;
    }
    const edit = input_edit_for_fragments(fragments, input_length);
    const old_tree = fragments[0].tree;

    if (edit) {
      const edited_old_ts_tree = old_tree.prop(TS_TREE_PROP)?.copy();
      if (!edited_old_ts_tree) {
        log_error("expected old tree when there is an edit");
        return null;
      }
      assert(
        input_length - old_tree.length === edit.newEndIndex - edit.oldEndIndex,
        "expect offset to match change in text length",
      );
      edited_old_ts_tree.edit(edit);
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
  static #extend_change(
    change: ChangeDetails,
    ts_tree: TSTree,
  ): Pick<ChangeDetails, "edit" | "old_tree"> {
    const { edit, edited_old_ts_tree } = change;
    const changed_ranges = edited_old_ts_tree.getChangedRanges(ts_tree);
    if (!is_non_empty(changed_ranges)) {
      return change;
    }
    const new_end_index = Math.max(
      edit.newEndIndex,
      last_element(changed_ranges).endIndex,
    );
    const extended_edit = ts_edit(
      Math.min(edit.startIndex, changed_ranges[0].startIndex),
      new_end_index + (edit.oldEndIndex - edit.newEndIndex),
      new_end_index,
    );
    return {
      edit: extended_edit,
      old_tree: change.old_tree,
    };
  }

  advance(): Tree | null {
    const { cache, fragments, input, stoppedAt, ts_parser } = this;
    const cm_text =
      input instanceof DocInput && stoppedAt == null ? input.doc : null;
    if (cm_text) {
      const cached = cache.get(cm_text);
      if (cached) {
        this.parsedPos = input.length;
        return cached;
      }
    }

    const text = input.read(0, stoppedAt ?? input.length);
    const input_length = text.length;

    const change = Parse.#change_details(fragments, input_length);
    let ts_tree = ts_parser.parse(text, change?.edited_old_ts_tree);
    let extended_change = null;
    if (ts_tree?.rootNode.endIndex === input_length) {
      extended_change = change ? Parse.#extend_change(change, ts_tree) : null;
    } else {
      // The edit was wrong, so do not use it to reuse parts of the old tree.
      log_error(
        "Mismatch between tree (%s) and document (%s) lengths; reparsing",
        ts_tree?.rootNode.endIndex,
        input_length,
      );
      ts_tree?.delete();
      ts_tree = ts_parser.parse(text);
    }
    change?.edited_old_ts_tree.delete();
    if (ts_tree == null) {
      return null;
    }

    // Convert the Lezer tree to a tree-sitter tree.
    const tree = this.#convert_tree(ts_tree, extended_change);
    this.parsedPos = input_length;
    if (cm_text) {
      cache.set(cm_text, tree);
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
  #node_types: NodeType[];
  /**
   * A parse can be started for the same document multiple times.
   *
   * For full parses, we can reuse these trees here.
   */
  #cache = new WeakMap<Text, Tree>();
  readonly ts_parser: TSParser;

  constructor(ts_parser: TSParser, props: NodePropSource[], top_node: string) {
    super();
    this.ts_parser = ts_parser;

    const { language } = ts_parser;
    if (language == null) {
      throw new MissingLanguageError();
    }
    this.#node_types = language.types.map((name, id) =>
      NodeType.define({ id, name, props, top: name === top_node }),
    );
  }

  createParse(
    input: Input,
    fragments: readonly TreeFragment[],
    ranges: readonly { from: number; to: number }[],
  ): PartialParse {
    return new Parse(
      this.ts_parser,
      this.#node_types,
      this.#cache,
      input,
      fragments,
      ranges,
    );
  }
}
