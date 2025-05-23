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
  }

  let { node }: Props = $props();

  let { account, children } = $derived(node);
  let is_toggled = $derived($toggled_accounts.has(account));
</script>

<span class="droptarget" data-account-name={account}>
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
