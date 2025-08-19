import { derived, get, writable } from "svelte/store";

import { dirnameBasename } from "../../lib/paths.ts";
import {
  buildSourcesTree,
  isDirectoryNode,
  type SourceNode,
} from "../../lib/sources.ts";
import { sources } from "../../stores/options.ts";

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
        (node: SourceNode) =>
          isDirectoryNode(node) && node.path.startsWith(directory),
      );

      for (const node of descendants) {
        newExpandedDirectories.set(node.path, expand);
      }
    } else if (event.ctrlKey || event.metaKey) {
      const directChildren = allMatching(
        $sourcesTree,
        (node: SourceNode) =>
          isDirectoryNode(node) && parent(node.path) === directory,
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
