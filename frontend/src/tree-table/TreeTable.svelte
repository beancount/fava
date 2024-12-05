<script lang="ts">
  import { writable } from "svelte/store";

  import type { AccountTreeNode } from "../charts/hierarchy";
  import { _ } from "../i18n";
  import { currency_name, operating_currency } from "../stores";
  import { collapse_account, invert_account } from "../stores/accounts";
  import AccountCellHeader from "./AccountCellHeader.svelte";
  import { get_collapsed, get_not_shown, setTreeTableContext } from "./helpers";
  import TreeTableNode from "./TreeTableNode.svelte";

  interface Props {
    /** The account tree to show. */
    tree: AccountTreeNode;
    /** The end date (for closed accounts). */
    end: Date | null;
  }

  let { tree, end }: Props = $props();

  // Initialize context.
  // toggled is computed once on initialisation; not_shown is kept updated.
  const toggled = writable(get_collapsed(tree, $collapse_account));
  const not_shown = writable(new Set<string>());
  setTreeTableContext({ toggled, not_shown });

  $not_shown = $get_not_shown(tree, end);
</script>

<ol
  class="flex-table tree-table-new"
  class:wider={$operating_currency.length > 1}
>
  <li class="head">
    <p>
      <AccountCellHeader />
      {#each $operating_currency as currency}
        <span class="num" title={$currency_name(currency)}>{currency}</span>
      {/each}
      <span class="num other">{_("Other")}</span>
    </p>
  </li>
  {#each tree.account === "" ? tree.children : [tree] as n}
    <TreeTableNode node={n} invert={$invert_account(n.account) ? -1 : 1} />
  {/each}
</ol>

<style>
  /* For two or more operating currencies, set a slightly smaller size. */
  .wider {
    font-size: 0.9em;
  }
</style>
