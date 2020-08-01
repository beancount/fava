<script>
  import { createEventDispatcher } from "svelte";

  import { selectedAccount } from "./stores";

  /** @type {import("./util").Node} */
  export let node;

  const expanded = true;
  let drag = false;

  function click() {
    $selectedAccount = $selectedAccount === node.fullname ? "" : node.fullname;
  }

  /**
   * Start drag if a document filename is dragged onto an account.
   * @param {DragEvent} event
   */
  function dragenter(event) {
    if (
      event.dataTransfer &&
      event.dataTransfer.types.includes("fava/filename")
    ) {
      event.preventDefault();
      drag = true;
    }
  }
  const dragover = dragenter;

  const dispatch = createEventDispatcher();

  /**
   * Handle a drop and bubble the event.
   * @param {DragEvent} event
   */
  function drop(event) {
    const filename =
      event.dataTransfer && event.dataTransfer.getData("fava/filename");
    if (filename) {
      dispatch("drop", { account: node.fullname, filename });
      drag = false;
    }
  }
</script>

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

{#if node.name}
  <p
    on:click={click}
    on:dragenter={dragenter}
    on:dragover={dragover}
    on:dragleave={() => {
      drag = false;
    }}
    on:drop|preventDefault={drop}
    title={node.fullname}
    class="droptarget"
    data-account-name={node.fullname}
    class:expanded
    class:selected={$selectedAccount === node.fullname}
    class:drag>
    <span>{node.name}</span>
  </p>
{/if}

{#if node.children.size}
  <ul class="flex-table" hidden={!expanded}>
    {#each [...node.children.values()] as child}
      <li>
        {#if node.children.size}
          <svelte:self on:drop node={child} />
        {:else}node.name{/if}
      </li>
    {/each}
  </ul>
{/if}
