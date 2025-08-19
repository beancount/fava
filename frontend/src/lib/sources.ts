import { dirnameBasename } from "./paths.ts";
import { stratify, type TreeNode } from "./tree.ts";

export type SourceNode = TreeNode<{ name: string; path: string }>;

export function isDirectoryNode(node: SourceNode): boolean {
  return node.children.length > 0;
}

export function buildSourcesTree(sources: Set<string>): SourceNode {
  const root = stratify(
    sources,
    (path) => path,
    (path) => ({ name: basename(path), path }),
    (path) => parent(path),
  );
  // Simplify the tree by removing the nodes with only one children
  return compressTree(root);
}

function basename(path: string): string {
  const [_, basename] = dirnameBasename(path);
  return basename;
}

function parent(path: string): string {
  const [dirname, _] = dirnameBasename(path);
  return dirname;
}

function compressTree(parent: SourceNode): SourceNode {
  if (parent.children.length === 0) {
    return parent;
  }

  if (parent.children.length === 1 && parent.children[0] !== undefined) {
    const onlyChild: SourceNode = parent.children[0];
    // Do not compress leaf nodes (=files)
    if (onlyChild.children.length === 0) {
      return parent;
    }

    const newName = parent.name + onlyChild.name;
    return compressTree(
      { name: newName, path: onlyChild.path, children: onlyChild.children },
    );
  } else {
    const newChildren: SourceNode[] = [];
    for (const child of parent.children) {
      newChildren.push(compressTree(child));
    }
    return { name: parent.name, path: parent.path, children: newChildren };
  }
}

