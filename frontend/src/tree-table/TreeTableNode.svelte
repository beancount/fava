<script lang="ts">
  import type { AccountTreeNode } from "../charts/hierarchy";
  import { is_empty } from "../lib/objects";
  import { currency_name, operating_currency } from "../stores";
  import { ctx } from "../stores/format";
  import AccountCell from "./AccountCell.svelte";
  import Diff from "./Diff.svelte";
  import { getTreeTableContext } from "./helpers";
  import TreeTableNode from "./TreeTableNode.svelte";

  interface Props {
    /** The account node to show. */
    node: AccountTreeNode;
    /** Whther to invert all numbers (either `1` or `-1`). */
    invert: number;
  }

  let { node, invert }: Props = $props();

  const { toggled, not_shown } = getTreeTableContext();

  let { account, children } = $derived(node);

  let is_toggled = $derived($toggled.has(account));

  let has_balance = $derived(!is_empty(node.balance));
  /** Whether to show the balance (or balance_children) */
  let show_balance = $derived(!is_toggled && has_balance);
  let shown_balance = $derived(
    show_balance ? node.balance : node.balance_children,
  );
  let shown_cost = $derived(show_balance ? node.cost : node.cost_children);
  let shown_balance_other = $derived(
    Object.entries(shown_balance)
      .sort()
      .filter(([c]) => !$operating_currency.includes(c)),
  );
  let dimmed = $derived(!is_toggled && !has_balance);
</script>

<li>
  <p>
    <AccountCell {node} />
    {#each $operating_currency as currency}
      {@const num = shown_balance[currency]}
      {@const cost_num = shown_cost?.[currency] ?? 0}
      <span class="num" class:dimmed>
        {#if num}
          {$ctx.num(invert * num, currency)}
          {#if cost_num && num - cost_num}
            {@const diff = invert * (num - cost_num)}
            <Diff {diff} num={invert * cost_num} {currency} />
          {/if}
        {/if}
      </span>
    {/each}
    <span class="num other" class:dimmed>
      {#each shown_balance_other as [currency, num]}
        {@const cost_num = shown_cost?.[currency] ?? 0}
        <span title={$currency_name(currency)}>
          {$ctx.amount(invert * num, currency)}
        </span>
        {#if cost_num && num - cost_num}
          {@const diff = invert * (num - cost_num)}
          <Diff {diff} num={invert * cost_num} {currency} />
        {/if}
        <br />
      {/each}
    </span>
  </p>
  {#if !is_toggled && children.some((n) => !$not_shown.has(n.account))}
    <ol>
      {#each children.filter((n) => !$not_shown.has(n.account)) as child (child.account)}
        <TreeTableNode node={child} {invert} />
      {/each}
    </ol>
  {/if}
</li>
