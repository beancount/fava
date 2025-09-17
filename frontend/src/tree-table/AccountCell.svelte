<!--
    @component
    Account name cell.
-->
<script lang="ts">
  import type { AccountTreeNode } from "../charts/hierarchy";
  import { urlForAccount } from "../helpers";
  import { leaf } from "../lib/account";
  import AccountIndicator from "../sidebar/AccountIndicator.svelte";
  import { toggle_account, toggled_accounts } from "../stores/accounts";

  interface Props {
    /** The account node to render the name cell for. */
    node: AccountTreeNode;
    /** The chain of folded accounts. If not given, defaults to `[node]`. */
    chain?: readonly AccountTreeNode[];
  }

  let { node, chain = [node] }: Props = $props();

  let { account, children } = $derived(node);
  let is_toggled = $derived($toggled_accounts.has(account));
</script>

<span class="account-cell droptarget" data-account-name={account}>
  {#if children.length > 0}
    <button
      type="button"
      class="unset"
      onclick={(event) => {
        toggle_account(account, event);
      }}
    >
      {is_toggled ? "▸" : "▾"}
    </button>
  {/if}
  <span class="account-name">
    {#each chain as link_node, i (link_node.account)}
      <a href={$urlForAccount(link_node.account)} class="account">
        {leaf(link_node.account)}
      </a>
      {#if i < chain.length - 1}
        <span class="sep">/</span>
      {/if}
    {/each}
  </span>
  <AccountIndicator {account} small />
</span>

<style>
  button {
    position: absolute;
    padding: 0 3px;
    color: var(--treetable-expander);
  }

  .account-name {
    display: inline-flex;
    flex-wrap: wrap;
    margin-left: 1em;
  }

  .sep {
    padding: 0 0.2em;
    opacity: 0.6;
  }

  .account-cell {
    display: flex;
    flex: 1;
    align-items: center;
    min-width: calc(14em - var(--account-indent, 0em));
    max-width: calc(30em - var(--account-indent, 0em));
    margin-left: var(--account-indent, 0);
  }

  /* Indent each level of account by one more 1em. */
  :global(ol ol) .account-cell {
    --account-indent: 1em;
  }

  :global(ol ol ol) .account-cell {
    --account-indent: 2em;
  }

  :global(ol ol ol ol) .account-cell {
    --account-indent: 3em;
  }

  :global(ol ol ol ol ol) .account-cell {
    --account-indent: 4em;
  }

  :global(ol ol ol ol ol ol) .account-cell {
    --account-indent: 5em;
  }

  :global(ol ol ol ol ol ol ol) .account-cell {
    --account-indent: 6em;
  }

  :global(ol ol ol ol ol ol ol ol) .account-cell {
    --account-indent: 7em;
  }

  :global(ol ol ol ol ol ol ol ol ol) .account-cell {
    --account-indent: 8em;
  }
</style>
