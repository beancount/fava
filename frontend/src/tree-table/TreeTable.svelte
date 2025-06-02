<script lang="ts">
  import { writable } from "svelte/store";

  import type { AccountTreeNode } from "../charts/hierarchy";
  import { _ } from "../i18n";
  import { currency_name } from "../stores";
  import { invert_account } from "../stores/accounts";
  import { operating_currency } from "../stores/options";
  import AccountCellHeader from "./AccountCellHeader.svelte";
  import { get_not_shown, setTreeTableNotShownContext } from "./helpers";
  import TreeTableNode from "./TreeTableNode.svelte";

  interface Props {
    /** The account tree to show. */
    tree: AccountTreeNode;
    /** The end date (for closed accounts). */
    end: Date | null;
  }

  let { tree, end }: Props = $props();
  let account = $derived(tree.account);

  const not_shown = writable(new Set<string>());
  setTreeTableNotShownContext(not_shown);

  $effect(() => {
    $not_shown = $get_not_shown(tree, end);
  });
</script>

<ol
  class="flex-table tree-table-new"
  class:wider={$operating_currency.length > 1}
>
  <li class="head">
    <p>
      <AccountCellHeader {account} />
      {#each $operating_currency as currency (currency)}
        <span class="num" title={$currency_name(currency)}>{currency}</span>
      {/each}
      <span class="num other">{_("Other")}</span>
    </p>
  </li>
  {#each account === "" ? tree.children : [tree] as node (node.account)}
    <TreeTableNode {node} invert={$invert_account(node.account) ? -1 : 1} />
  {/each}
</ol>

<style>
  /* For two or more operating currencies, set a slightly smaller size. */
  .wider {
    font-size: 0.9em;
  }
</style>
