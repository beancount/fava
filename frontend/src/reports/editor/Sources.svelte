<script lang="ts">
  import type { SourceNode } from "../../lib/sources.ts";
  import Sources from "./Sources.svelte";
  import {
    expandedDirectories,
    sourcesTree,
    toggleDirectory,
  } from "./stores.ts";

  interface Props {
    isRoot?: boolean;
    node?: SourceNode;
    sourceSelectionAction: (source: string) => void;
    selectedSourcePath: string;
  }

  let {
    isRoot = false,
    node,
    sourceSelectionAction,
    selectedSourcePath,
  }: Props = $props();

  // If $sourcesTree was the default argument for node,
  // we would not get updates to the tree if files change.
  // node is undefined only when we are adding the root from EditorMenu.
  let derivedNode: SourceNode = $derived(
    isRoot
      ? $sourcesTree
      : (node ?? { name: "error", path: "error", children: [] }),
  );

  let nodeName: string = $derived(derivedNode.name);
  let nodePath: string = $derived(derivedNode.path);
  let isExpanded: boolean = $derived.by(() => {
    const result = $expandedDirectories.get(nodePath);
    // Even though root is always expanded, treat is as being collapsed by default.
    // This allows for expanding everything with one Ctrl/Meta-Click. The subsequent click would then collapse everything.
    return result ?? (!isRoot && selectedSourcePath.startsWith(nodePath));
  });

  let isDirectory: boolean = $derived(derivedNode.children.length > 0);
  let selected: boolean = $derived.by(() => {
    // Show where the selected file would be, if directories are collapsed
    if (isDirectory && !isExpanded && !isRoot) {
      return selectedSourcePath.startsWith(nodePath);
    }
    return selectedSourcePath === nodePath;
  });

  let action = (event: MouseEvent) => {
    if (isDirectory) {
      toggleDirectory(nodePath, !isExpanded, event);
    } else {
      sourceSelectionAction(nodePath);
    }
    event.stopPropagation();
  };
</script>

<li class:selected role="menuitem">
  {#if isRoot}
    <button
      type="button"
      title="Beancount data root directory
Shift-Click to expand/collapse immediate directories
Ctrl-/Cmd-/Meta-Click to expand/collapse all directories."
      class="unset root"
      onclick={action}>{nodeName}</button
    >
  {:else}
    <p>
      {#if isDirectory}
        <button type="button" class="unset toggle" onclick={action}
          >{isExpanded ? "▾" : "▸"}</button
        >
      {/if}
      <button type="button" class="unset leaf" onclick={action}
        >{nodeName}</button
      >
    </p>
  {/if}
  {#if isDirectory && (isExpanded || isRoot)}
    <ul>
      {#each derivedNode.children as child (child.path)}
        <Sources node={child} {sourceSelectionAction} {selectedSourcePath} />
      {/each}
    </ul>
  {/if}
</li>

<style>
  ul {
    padding: 0 0 0 0.5em;
    margin: 0;
  }

  p {
    position: relative;
    display: flex;
    padding-right: 0.5em;
    margin: 0;
    overflow: hidden;
    border-bottom: 1px solid var(--table-border);
    border-left: 1px solid var(--table-border);
  }

  p > * {
    padding: 1px;
  }

  .selected {
    background-color: var(--table-header-background);
  }

  .leaf {
    flex-grow: 1;
    margin-left: 1em;
  }

  .toggle {
    position: absolute;
    margin: 0 0.25rem;
    color: var(--treetable-expander);
  }

  .root {
    margin: 0 0.25rem;
    font-size: 90%;
  }
</style>
