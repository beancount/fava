/**
 * A tree node.
 *
 * The only base property this has is `.children`, all others are
 * passed in via the generic parameter.
 */
export type TreeNode<S> = S & { children: TreeNode<S>[] };

/**
 * Obtain the parent account name.
 * @param name - an account name.
 */
export function parentAccount(name: string): string {
  const parentEnd = name.lastIndexOf(":");
  return parentEnd > 0 ? name.slice(0, parentEnd) : "";
}

/**
 * Obtain the leaf part of the account name.
 * @param name - an account name.
 */
export function leafAccount(name: string): string {
  const parentEnd = name.lastIndexOf(":");
  return parentEnd > 0 ? name.slice(parentEnd + 1) : name;
}

/**
 * Generate an account tree from an array.
 *
 * This is a bit like d3-hierarchys stratify, but inserts implicit nodes that
 * are missing in the hierarchy.
 *
 * @param data - the data to generate the tree for.
 * @param id - A getter to obtain the node name for an input datum.
 * @param init - A getter for any extra properties to set on the node.
 */
export function stratify<T, S = null>(
  data: Iterable<T>,
  id: (datum: T) => string,
  init: (name: string, datum?: T) => S
): TreeNode<S> {
  const root: TreeNode<S> = { children: [], ...init("") };
  const map = new Map<string, TreeNode<S>>();
  map.set("", root);

  function addAccount(name: string, datum?: T): TreeNode<S> {
    const existing = map.get(name);
    if (existing) {
      Object.assign(existing, init(name, datum));
      return existing;
    }
    const node: TreeNode<S> = { children: [], ...init(name, datum) };
    map.set(name, node);
    const parentName = parentAccount(name);
    const parent = map.get(parentName) ?? addAccount(parentName);
    parent.children.push(node);
    return node;
  }

  [...data]
    .sort((a, b) => id(a).localeCompare(id(b)))
    .forEach((datum) => addAccount(id(datum), datum));
  return root;
}

/**
 * Generate an account tree from an array of entries.
 */
export function entriesToTree<T extends { account: string }>(
  data: T[]
): TreeNode<Record<string, unknown>> {
  return stratify(
    new Set(data.map((e) => e.account)),
    (s) => s,
    (name) => ({ name })
  );
}
