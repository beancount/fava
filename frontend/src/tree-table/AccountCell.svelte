<!--
    @component
    Account name cell.
-->
<script lang="ts">
  import type { AccountTreeNode } from "../charts/hierarchy.ts";
  import { urlForAccount } from "../helpers.ts";
  import { leaf } from "../lib/account.ts";
  import AccountIndicator from "../sidebar/AccountIndicator.svelte";
  import { toggle_account, toggled_accounts } from "../stores/accounts.ts";

  interface Props {
    /** The account node to render the name cell for. */
    node: AccountTreeNode;
  }

  let { node }: Props = $props();

  let { account, children } = $derived(node);
  let is_toggled = $derived($toggled_accounts.has(account));
  const level = $derived(String(account.split(":").length - 1));
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
  <a href={$urlForAccount(account)} class="account acclevel{level}">
    {leaf(account)}
  </a>
  <AccountIndicator {account} small />
</span>

<style>
  button {
    position: absolute;
    padding: 0 3px;
    font-size: 17px;
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

  .acclevel1 {
    /* font-size: 16px; */
    font-weight: 600;
  }

  .acclevel2 {
    font-weight: 600;
    opacity: 0.7;
  }

  /* Indent each level of account by one more 1em. */
  :global(ol ol) span {
    --account-indent: 1em;

    font-weight: 700;
  }

  :global(ol ol ol) span {
    --account-indent: 2em;

    font-weight: 700;
    opacity: 0.7; /* Will be inherited to levels below */
  }

  :global(ol ol ol ol) span {
    --account-indent: 3em;

    font-weight: 500; /* Will be inherited to levels below */
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
