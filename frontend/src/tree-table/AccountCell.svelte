<!--
    @component
    Account name cell.
-->
<script lang="ts">
  import type { AccountTreeNode } from "../charts/hierarchy";
  import { urlForAccount } from "../helpers";
  import { leaf } from "../lib/account";
  import AccountIndicator from "../sidebar/AccountIndicator.svelte";
  import { getTreeTableContext } from "./helpers";

  /** The account node to render the name cell for. */
  export let node: AccountTreeNode;

  const { toggled } = getTreeTableContext();

  $: ({ account, children } = node);

  /**
   * Toggle the account and (depending on the mouse event) its children in the set.
   */
  $: on_click = (event: MouseEvent) => {
    toggled.update((t) => {
      const new_t = new Set(t);
      const is_toggled = new_t.has(account);
      if (is_toggled) {
        new_t.delete(account);
      } else {
        new_t.add(account);
      }
      if (event.shiftKey) {
        // toggle all children as well.
        const toggle_all = (n: AccountTreeNode) => {
          if (is_toggled) {
            new_t.delete(n.account);
          } else {
            new_t.add(n.account);
          }
          n.children.filter((c) => c.children.length).forEach(toggle_all);
        };
        children.forEach(toggle_all);
      }
      if (is_toggled && (event.ctrlKey || event.metaKey)) {
        // collapse all direct children to only expand one level
        children
          .filter((c) => c.children.length)
          .forEach((n) => {
            new_t.add(n.account);
          });
      }
      return new_t;
    });
  };
</script>

<span class="droptarget" data-account-name={account}>
  {#if children.length > 0}
    <button type="button" class="unset" on:click={on_click}>
      {$toggled.has(account) ? "▸" : "▾"}
    </button>
  {/if}
  <a href={$urlForAccount(account)} class="account">
    {leaf(account)}
  </a>
  <AccountIndicator {account} small />
</span>

<style>
  button {
    position: absolute;
    padding: 0 3px;
    color: var(--treetable-expander);
  }

  a {
    margin-left: 1em;
  }

  span {
    display: flex;
    flex: 1;
    align-items: center;
    min-width: calc(14em - var(--account-indent, 0em));
    max-width: calc(30em - var(--account-indent, 0em));
    margin-left: var(--account-indent, 0);
  }

  /* Indent each level of account by one more 1em. */
  :global(ol ol) span {
    --account-indent: 1em;
  }

  :global(ol ol ol) span {
    --account-indent: 2em;
  }

  :global(ol ol ol ol) span {
    --account-indent: 3em;
  }

  :global(ol ol ol ol ol) span {
    --account-indent: 4em;
  }

  :global(ol ol ol ol ol ol) span {
    --account-indent: 5em;
  }

  :global(ol ol ol ol ol ol ol) span {
    --account-indent: 6em;
  }

  :global(ol ol ol ol ol ol ol ol) span {
    --account-indent: 7em;
  }

  :global(ol ol ol ol ol ol ol ol ol) span {
    --account-indent: 8em;
  }
</style>
