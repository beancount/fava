<script lang="ts">
  import { leaf } from "../../lib/account";
  import type { TreeNode } from "../../lib/tree";
  import Accounts from "./Accounts.svelte";
  import { selectedAccount } from "./stores";

  interface Props {
    node: TreeNode<{ name: string; count: number }>;
    move: (m: { account: string; filename: string }) => void;
  }

  let { node, move }: Props = $props();

  let expanded = $state(true);
  let drag = $state(false);

  let hasChildren = $derived(node.children.length > 0);
  let selected = $derived($selectedAccount === node.name);

  /**
   * Start drag if a document filename is dragged onto an account.
   * @param event - The drag event that is passed to the event handler.
   */
  function dragenter(event: DragEvent) {
    const types = event.dataTransfer?.types ?? [];
    if (types.includes("fava/filename")) {
      event.preventDefault();
      drag = true;
    }
  }

  /**
   * Handle a drop and bubble the event.
   * @param event - The drag event that is passed to the event handler.
   */
  function drop(event: DragEvent) {
    event.preventDefault();
    const filename = event.dataTransfer?.getData("fava/filename");
    if (filename != null) {
      move({ account: node.name, filename });
      drag = false;
    }
  }
</script>

{#if node.name}
  <p
    ondragenter={dragenter}
    ondragover={dragenter}
    ondragleave={() => {
      drag = false;
    }}
    ondrop={drop}
    title={node.name}
    class="droptarget"
    data-account-name={node.name}
    class:selected
    class:drag
  >
    {#if hasChildren}
      <button
        type="button"
        class="unset toggle"
        onclick={(ev) => {
          expanded = !expanded;
          ev.stopPropagation();
        }}>{expanded ? "▾" : "▸"}</button
      >
    {/if}
    <button
      type="button"
      class="unset leaf"
      onclick={() => {
        $selectedAccount = selected ? "" : node.name;
      }}>{leaf(node.name)}</button
    >
    {#if node.count > 0}
      <span class="count"> {node.count}</span>
    {/if}
  </p>
{/if}
{#if hasChildren}
  <ul hidden={!expanded}>
    {#each node.children as child}
      <li>
        <Accounts node={child} {move} />
      </li>
    {/each}
  </ul>
{/if}

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

  .count {
    opacity: 0.6;
  }

  .selected,
  .drag {
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
</style>
