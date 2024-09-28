<script lang="ts">
  import type { AccountBudget } from "../api/validators";
  import type { AccountTreeNode } from "../charts/hierarchy";
  import type { NonEmptyArray } from "../lib/array";
  import { is_empty } from "../lib/objects";
  import { currency_name } from "../stores";
  import { ctx } from "../stores/format";
  import AccountCell from "./AccountCell.svelte";
  import Diff from "./Diff.svelte";
  import { getTreeTableContext } from "./helpers";

  /** The account nodes to show. */
  export let nodes: NonEmptyArray<AccountTreeNode>;
  /** The budgets (per account a list per date range). */
  export let budgets: Record<string, AccountBudget[]>;

  const { toggled, not_shown } = getTreeTableContext();

  $: [node] = nodes;
  $: ({ account, children } = node);
  $: account_budgets = budgets[account];

  $: is_toggled = $toggled.has(account);
</script>

<li>
  <p>
    <AccountCell {node} />
    {#each nodes as n, index}
      {@const account_budget = account_budgets?.[index]}
      {@const has_balance =
        !is_empty(n.balance) ||
        (account_budget != null && !is_empty(account_budget.budget))}
      {@const show_balance = !is_toggled && has_balance}
      {@const shown_balance = show_balance ? n.balance : n.balance_children}
      {@const shown_budget = show_balance
        ? account_budget?.budget
        : account_budget?.budget_children}
      <span class="num other" class:dimmed={!is_toggled && !has_balance}>
        {#each Object.entries(shown_balance) as [currency, number]}
          {@const budget = shown_budget?.[currency]}
          <span title={$currency_name(currency)}>
            {$ctx.amount(number, currency)}
          </span>
          {#if budget}
            <Diff diff={budget - number} num={budget} {currency} />
          {/if}
          <br />
        {/each}
        {#if shown_budget}
          {#each Object.entries(shown_budget).filter(([c]) => !(shown_balance[c] ?? 0)) as [currency, budget]}
            <span title={$currency_name(currency)}>
              {$ctx.amount(0, currency)}
            </span>
            <Diff diff={budget} num={budget} {currency} />
            <br />
          {/each}
        {/if}
      </span>
    {/each}
  </p>
  {#if !is_toggled && children.some((n) => !$not_shown.has(n.account))}
    <ol>
      {#each children as child, index (child.account)}
        {#if !$not_shown.has(child.account)}
          <svelte:self nodes={nodes.map((n) => n.children[index])} {budgets} />
        {/if}
      {/each}
    </ol>
  {/if}
</li>
