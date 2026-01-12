<script lang="ts">
  import type { SourceNode } from "../../lib/sources.ts";
  import Sources from "./Sources.svelte";
  import { expanded_directories, toggle_directory } from "./stores.ts";

  interface Props {
    is_root?: boolean;
    node: SourceNode;
    on_select: (source: string) => void;
    selected: string;
  }

  let { is_root = false, node, on_select, selected }: Props = $props();

  let is_expanded = $derived.by(() => {
    const result = $expanded_directories.get(node.path);
    // Even though root is always expanded, treat is as being collapsed by default.
    // This allows for expanding everything with one Ctrl/Meta-Click. The subsequent click would then collapse everything.
    return result ?? (!is_root && selected.startsWith(node.path));
  });

  let is_directory = $derived(node.children.length > 0);
  // Show where the selected file would be, if directories are collapsed
  let is_selected = $derived(
    is_directory && !is_expanded && !is_root
      ? selected.startsWith(node.path)
      : selected === node.path,
  );

  let action = (event: MouseEvent) => {
    if (is_directory) {
      toggle_directory(node.path, !is_expanded, event);
    } else {
      on_select(node.path);
    }
    event.stopPropagation();
  };
</script>

<li class:selected={is_selected} role="menuitem">
  {#if is_root}
    <button
      type="button"
      title="Beancount data root directory
Shift-Click to expand/collapse immediate directories
Ctrl-/Cmd-/Meta-Click to expand/collapse all directories."
      class="unset root"
      onclick={action}
    >
      {node.name}
    </button>
  {:else}
    <p>
      {#if is_directory}
        <button type="button" class="unset toggle" onclick={action}>
          {is_expanded ? "▾" : "▸"}
        </button>
      {/if}
      <button type="button" class="unset leaf" onclick={action}>
        {node.name}
      </button>
    </p>
  {/if}
  {#if is_directory && (is_expanded || is_root)}
    <ul>
      {#each node.children as child (child.path)}
        <Sources node={child} {on_select} {selected} />
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
  }
</style>
