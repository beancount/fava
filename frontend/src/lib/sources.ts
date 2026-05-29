import { basename, split } from "./paths.ts";
import { stratify, type TreeNode } from "./tree.ts";

export type SourceNode = TreeNode<{ name: string; path: string }>;

export function is_directory(node: SourceNode): boolean {
  return node.children.length > 0;
}

export function build_compressed_sources_tree(
  sources: Set<string>,
): SourceNode {
  const root = stratify(
    sources,
    (path) => path,
    (path) => ({ name: basename(path), path }),
    (path) => split(path)[0],
  );
  return compress_tree(root);
}

/** Simplify the tree by removing the nodes with only one child. */
function compress_tree(parent: SourceNode): SourceNode {
  const { children, name, path } = parent;

  if (children.length === 0) {
    return parent;
  }

  const [first_child] = children;
  if (children.length === 1 && first_child != null) {
    // Do not compress leaf nodes (=files)
    if (first_child.children.length === 0) {
      return parent;
    }

    return compress_tree({
      name: name + first_child.name,
      path: first_child.path,
      children: first_child.children,
    });
  } else {
    return { name, path, children: children.map(compress_tree) };
  }
}
