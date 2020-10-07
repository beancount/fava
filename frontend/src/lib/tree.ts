export interface Node {
  name: string;
  children: Node[];
}

export function parentAccount(name: string): string {
  const parentEnd = name.lastIndexOf(":");
  return parentEnd > 0 ? name.slice(0, parentEnd) : "";
}

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
 */
export function stratify<T>(data: T[], id: (d: T) => string): Node {
  const root: Node = { name: "", children: [] };
  const map = new Map<string, Node>();
  map.set(root.name, root);

  function addAccount(name: string): Node {
    const existing = map.get(name);
    if (existing) {
      return existing;
    }
    const node: Node = { name, children: [] };
    map.set(name, node);
    const parentName = parentAccount(name);
    const parent = map.get(parentName) ?? addAccount(parentName);
    parent.children.push(node);
    return node;
  }

  for (const account of data) {
    addAccount(id(account));
  }
  return root;
}

/**
 * Generate an account tree from an array of entries.
 */
export function entriesToTree<T extends { account: string }>(data: T[]): Node {
  const accounts = new Set(data.map((e) => e.account));
  return stratify([...accounts].sort(), (s) => s);
}
