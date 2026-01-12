import { parent as parentAccount } from "./account.ts";

/**
 * A tree node.
 *
 * The only base property this has is `.children`, all others are
 * passed in via the generic parameter.
 */
export type TreeNode<S> = S & { readonly children: TreeNode<S>[] };

/**
 * Generate an account tree from an array. The data will be sorted.
 *
 * This is a bit like d3-hierarchys stratify, but inserts implicit nodes that
 * are missing in the hierarchy.
 *
 * @param data - the data (accounts) to generate the tree for.
 * @param id - A getter to obtain the node name for an input datum.
 * @param init - A getter for any extra properties to set on the node.
 */
export function stratifyAccounts<T, S = null>(
  data: Iterable<T>,
  id: (datum: T) => string,
  init: (name: string, datum?: T) => S,
): TreeNode<S> {
  return stratify(
    [...data].sort((a, b) => id(a).localeCompare(id(b))),
    id,
    init,
    parentAccount,
  );
}

/**
 * Generate a tree from an array. The data will not be sorted.
 *
 * This is a bit like d3-hierarchys stratify, but inserts implicit nodes that
 * are missing in the hierarchy.
 *
 * @param data - the data to generate the tree for.
 * @param id - A getter to obtain the node name for an input datum.
 * @param init - A getter for any extra properties to set on the node.
 * @param parent - A getter to obtain the parent node name.
 */
export function stratify<T, S = null>(
  data: Iterable<T>,
  id: (datum: T) => string,
  init: (name: string, datum?: T) => S,
  parent: (name: string) => string,
): TreeNode<S> {
  const root: TreeNode<S> = { children: [], ...init("") };
  const map = new Map<string, TreeNode<S>>();
  map.set("", root);

  function addNode(name: string, datum?: T): TreeNode<S> {
    const existing = map.get(name);
    if (existing) {
      Object.assign(existing, init(name, datum));
      return existing;
    }
    const node: TreeNode<S> = { children: [], ...init(name, datum) };
    map.set(name, node);
    const parentName = parent(name);
    const parentNode = map.get(parentName) ?? addNode(parentName);
    parentNode.children.push(node);
    return node;
  }

  [...data].forEach((datum) => {
    addNode(id(datum), datum);
  });
  return root;
}

/**
 * Get all matching descendants.
 */
export function* all_matching<T>(
  root: TreeNode<T>,
  predicate: (node: TreeNode<T>) => boolean,
): Generator<TreeNode<T>, void, void> {
  if (predicate(root)) {
    yield root;
  }
  for (const child of root.children) {
    for (const match of all_matching(child, predicate)) {
      yield match;
    }
  }
}
