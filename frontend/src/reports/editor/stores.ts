import { derived, get, writable } from "svelte/store";

import { sources } from "../../stores/options";

export class SourceNode {
  name: string;
  path: string;
  children: SourceNode[];

  constructor(name: string, path: string, children: SourceNode[] = []) {
    this.name = name;
    this.path = path;
    this.children = children;
  }

  isDirectory(): boolean {
    return this.children.length > 0;
  }
}

function buildSourcesTree($sources: Set<string>): SourceNode {
  const map = new Map<string, SourceNode>();
  const root = new SourceNode("", "");
  map.set("", root);

  function addNode(path: string): SourceNode {
    const [dirname, basename] = dirnameBasename(path);
    const node = new SourceNode(basename, path);
    map.set(path, node);
    const parent = map.get(dirname) ?? addNode(dirname);
    parent.children.push(node);
    return node;
  }

  $sources.forEach((source) => {
    addNode(source);
  });

  // Simplify the tree by removing the nodes with only one children
  return compressTree(root);
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
      new SourceNode(newName, onlyChild.path, onlyChild.children),
    );
  } else {
    const newChildren: SourceNode[] = [];
    for (const child of parent.children) {
      newChildren.push(compressTree(child));
    }
    return new SourceNode(parent.name, parent.path, newChildren);
  }
}

export const sourcesTree = derived(sources, ($sources) => {
  return buildSourcesTree($sources);
});

// The directories which have been explicitly expanded (true) or collapsed (false).
export const expandedDirectories = writable<ReadonlyMap<string, boolean>>(
  new Map(),
);

/**
 * Toggle a directory.
 *
 * If Shift-Click, deeply expand/collapse all descendants.
 * If Ctrl- or Meta-Click, expand/collapse direct children.
 */
export function toggleDirectory(
  directory: string,
  expand: boolean,
  event: MouseEvent,
): void {
  const $sourcesTree: SourceNode = get(sourcesTree);

  expandedDirectories.update(($expandedDirectories) => {
    const newExpandedDirectories = new Map($expandedDirectories);
    newExpandedDirectories.set(directory, expand);
    if (event.shiftKey) {
      const descendants = allMatching(
        $sourcesTree,
        (node) => node.isDirectory() && node.path.startsWith(directory),
      );

      for (const node of descendants) {
        newExpandedDirectories.set(node.path, expand);
      }
    } else if (event.ctrlKey || event.metaKey) {
      const directChildren = allMatching(
        $sourcesTree,
        (node) => node.isDirectory() && parent(node.path) === directory,
      );

      for (const node of directChildren) {
        newExpandedDirectories.set(node.path, expand);
      }
    }
    return newExpandedDirectories;
  });
}

function parent(path: string): string {
  const [dirname, _] = dirnameBasename(path);
  return dirname;
}

// Splits the path to dirname (including last separator) and basename
function dirnameBasename(path: string): [string, string] {
  // Special case for when we only have the last remaining separator i.e. root
  if (path.length < 2) {
    return ["", path];
  }
  // Handle both Windows and unix style path separators and a mixture of them
  const lastIndexOfSlash = path.lastIndexOf("/", path.length - 2);
  const lastIndexOfBackslash = path.lastIndexOf("\\", path.length - 2);
  const lastIndex =
    lastIndexOfSlash > lastIndexOfBackslash
      ? lastIndexOfSlash
      : lastIndexOfBackslash;
  // This could maybe happen on Windows if the path name is something like C:\
  if (lastIndex < 0) {
    return ["", path];
  }
  return [path.substring(0, lastIndex + 1), path.substring(lastIndex + 1)];
}

function* allMatching(
  root: SourceNode,
  predicate: (node: SourceNode) => boolean,
): Generator<SourceNode, void, void> {
  if (predicate(root)) {
    yield root;
  }
  for (const child of root.children) {
    for (const match of allMatching(child, predicate)) {
      yield match;
    }
  }
}
