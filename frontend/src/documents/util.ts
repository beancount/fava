import { group } from "d3-array";

export interface Node {
  name: string;
  fullname: string;
  children: Map<string, Node>;
}

/**
 * Generate an account tree from an array of entries.
 */
export function entriesToTree<T extends { account: string }>(data: T[]): Node {
  const groups = group(data, (e) => e.account);
  const root: Node = { name: "", fullname: "", children: new Map() };
  for (const account of [...groups.keys()].sort()) {
    let node: Node | undefined = root;
    let parent: Node;
    const parts = account.split(":");
    for (const part of parts) {
      parent = node;
      node = parent.children.get(part);
      if (!node) {
        node = {
          name: part,
          fullname: parent.fullname ? `${parent.fullname}:${part}` : part,
          children: new Map(),
        };
        parent.children.set(part, node);
      }
    }
  }
  return root;
}
