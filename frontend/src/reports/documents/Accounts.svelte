<script lang="ts">
  import { leaf } from "../../lib/account";
  import type { TreeNode } from "../../lib/tree";
  import { toggle_account, toggled_accounts } from "../../stores/accounts";
  import Accounts from "./Accounts.svelte";
  import { selectedAccount } from "./stores";

  interface Props {
    node: TreeNode<{ name: string; count: number }>;
    move: (m: { account: string; filename: string }) => void;
  }

  let { node, move }: Props = $props();
  let account = $derived(node.name);

  let drag = $state(false);
  let is_toggled = $derived($toggled_accounts.has(account));

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

{#if account}
  <p
    ondragenter={dragenter}
    ondragover={dragenter}
    ondragleave={() => {
      drag = false;
    }}
    ondrop={drop}
    title={account}
    class="droptarget"
    data-account-name={account}
    class:selected
    class:drag
  >
    {#if hasChildren}
      <button
        type="button"
        class="unset toggle"
        onclick={(event) => {
          toggle_account(account, event);
          event.stopPropagation();
        }}>{is_toggled ? "▸" : "▾"}</button
      >
    {/if}
    <button
      type="button"
      class="unset leaf"
      onclick={() => {
        $selectedAccount = selected ? "" : account;
      }}>{leaf(account)}</button
    >
    {#if node.count > 0}
      <span class="count"> {node.count}</span>
    {/if}
  </p>
{/if}
{#if hasChildren && !is_toggled}
  <ul>
    {#each node.children as child (child.name)}
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
