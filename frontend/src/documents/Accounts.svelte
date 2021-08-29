<script lang="ts">
  import { leaf } from "../lib/account";
  import type { TreeNode } from "../lib/tree";

  import { selectedAccount } from "./stores";

  export let node: TreeNode<{ name: string; count: number }>;
  export let move: (m: { account: string; filename: string }) => void;

  let expanded = true;
  let drag = false;

  $: hasChildren = node.children.length > 0;
  $: selected = $selectedAccount === node.name;

  /**
   * Start drag if a document filename is dragged onto an account.
   * @param event - The drag event that is passed to the event handler.
   */
  function dragenter(event: DragEvent) {
    if (event.dataTransfer?.types.includes("fava/filename")) {
      event.preventDefault();
      drag = true;
    }
  }

  /**
   * Handle a drop and bubble the event.
   * @param event - The drag event that is passed to the event handler.
   */
  function drop(event: DragEvent) {
    const filename = event.dataTransfer?.getData("fava/filename");
    if (filename) {
      move({ account: node.name, filename });
      drag = false;
    }
  }
</script>

{#if node.name}
  <p
    on:click={() => {
      $selectedAccount = selected ? "" : node.name;
    }}
    on:dragenter={dragenter}
    on:dragover={dragenter}
    on:dragleave={() => {
      drag = false;
    }}
    on:drop|preventDefault={drop}
    title={node.name}
    class="droptarget"
    data-account-name={node.name}
    class:has-children={hasChildren}
    class:selected
    class:drag
  >
    <span
      class="toggle"
      on:click={(ev) => {
        expanded = !expanded;
        ev.stopPropagation();
      }}>{expanded ? "▾" : "▸"}</span
    >
    <span>{leaf(node.name)}</span>
    {#if node.count > 0}
      <span class="spacer" />
      <span class="count"> {node.count}</span>
    {/if}
  </p>
{/if}

{#if hasChildren}
  <ul class="flex-table" hidden={!expanded}>
    {#each node.children as child}
      <li>
        <svelte:self node={child} {move} />
      </li>
    {/each}
  </ul>
{/if}

<style>
  ul {
    padding: 0 0 0 0.5em;
  }
  p {
    margin-bottom: -1px;
    overflow: hidden;
    cursor: pointer;
    border: 1px solid var(--color-table-border);
  }
  .count {
    opacity: 0.6;
  }
  .selected,
  .drag {
    background-color: var(--color-table-header-background);
  }
  .toggle {
    color: var(--color-treetable-expander);
    visibility: hidden;
  }
  .has-children > .toggle {
    visibility: visible;
  }
</style>
