<script lang="ts">
  import { leaf } from "../lib/account";
  import type { TreeNode } from "../lib/tree";

  import { selectedAccount } from "./stores";

  export let node: TreeNode<{ name: string }>;
  export let move: (m: { account: string; filename: string }) => void;

  const expanded = true;
  let drag = false;

  function click() {
    $selectedAccount = $selectedAccount === node.name ? "" : node.name;
  }

  /**
   * Start drag if a document filename is dragged onto an account.
   */
  function dragenter(event: DragEvent) {
    if (event.dataTransfer?.types.includes("fava/filename")) {
      event.preventDefault();
      drag = true;
    }
  }
  const dragover = dragenter;

  /**
   * Handle a drop and bubble the event.
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
    on:click={click}
    on:dragenter={dragenter}
    on:dragover={dragover}
    on:dragleave={() => {
      drag = false;
    }}
    on:drop|preventDefault={drop}
    title={node.name}
    class="droptarget"
    data-account-name={node.name}
    class:expanded
    class:selected={$selectedAccount === node.name}
    class:drag
  >
    <span>{leaf(node.name)}</span>
  </p>
{/if}

{#if node.children.length}
  <ul class="flex-table" hidden={!expanded}>
    {#each node.children as child}
      <li>
        {#if node.children.length}
          <svelte:self node={child} {move} />
        {:else}node.name{/if}
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
  .selected,
  .drag {
    background-color: var(--color-table-header-background);
  }
</style>
