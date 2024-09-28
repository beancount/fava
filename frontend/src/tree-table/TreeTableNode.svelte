<script lang="ts">
  import type { AccountTreeNode } from "../charts/hierarchy";
  import { is_empty } from "../lib/objects";
  import { currency_name, operating_currency } from "../stores";
  import { ctx } from "../stores/format";
  import AccountCell from "./AccountCell.svelte";
  import Diff from "./Diff.svelte";
  import { getTreeTableContext } from "./helpers";

  /** The account node to show. */
  export let node: AccountTreeNode;
  /** Whther to invert all numbers (either `1` or `-1`). */
  export let invert: number;

  const { toggled, not_shown } = getTreeTableContext();

  $: ({ account, children } = node);

  $: is_toggled = $toggled.has(account);

  $: has_balance = !is_empty(node.balance);
  /** Whether to show the balance (or balance_children) */
  $: show_balance = !is_toggled && has_balance;
  $: shown_balance = show_balance ? node.balance : node.balance_children;
  $: shown_cost = show_balance ? node.cost : node.cost_children;
  $: shown_balance_other = Object.entries(shown_balance)
    .sort()
    .filter(([c]) => !$operating_currency.includes(c));
  $: dimmed = !is_toggled && !has_balance;
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
        <svelte:self node={child} {invert} />
      {/each}
    </ol>
  {/if}
</li>
