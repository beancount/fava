<script lang="ts">
  import type { AccountTreeNode } from "../charts/hierarchy.ts";
  import { last_element, type NonEmptyArray } from "../lib/array.ts";
  import { is_empty } from "../lib/objects.ts";
  import { toggled_accounts } from "../stores/accounts.ts";
  import { ctx } from "../stores/format.ts";
  import { currency_name } from "../stores/index.ts";
  import { operating_currency } from "../stores/options.ts";
  import AccountCell from "./AccountCell.svelte";
  import Diff from "./Diff.svelte";
  import { getTreeTableNotShownContext } from "./helpers.ts";
  import TreeTableNode from "./TreeTableNode.svelte";

  interface Props {
    /** The account node to show. */
    node: AccountTreeNode;
    /** Whther to invert all numbers (either `1` or `-1`). */
    invert: number;
  }

  let { node, invert }: Props = $props();

  const not_shown = getTreeTableNotShownContext();

  function compute_fold_info(
    start_node: AccountTreeNode,
    not_shown_set: ReadonlySet<string>,
  ): NonEmptyArray<AccountTreeNode> {
    const chain: AccountTreeNode[] = [];
    let current: AccountTreeNode | undefined = start_node;
    do {
      chain.push(current);
      const visible_children: AccountTreeNode[] = current.children.filter(
        (n) => !not_shown_set.has(n.account),
      );
      current =
        visible_children.length === 1 && is_empty(current.balance)
          ? visible_children[0]
          : undefined;
    } while (current);
    return chain as readonly AccountTreeNode[] as NonEmptyArray<AccountTreeNode>;
  }

  let chain = $derived(compute_fold_info(node, $not_shown));
  let display_node = $derived(last_element(chain));
  let { account, children } = $derived(display_node);

  let is_toggled = $derived($toggled_accounts.has(account));

  let has_balance = $derived(!is_empty(display_node.balance));
  /** Whether to show the balance (or balance_children) */
  let show_balance = $derived(!is_toggled && has_balance);
  let shown_balance = $derived(
    show_balance ? display_node.balance : display_node.balance_children,
  );
  let shown_cost = $derived(
    show_balance ? display_node.cost : display_node.cost_children,
  );

  let shown_balance_other = $derived(
    Object.entries(shown_balance)
      .sort()
      .filter(([c]) => !$operating_currency.includes(c)),
  );
  let dimmed = $derived(!is_toggled && !has_balance);
</script>

<li>
  <p>
    <AccountCell node={display_node} {chain} />
    {#each $operating_currency as currency (currency)}
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
      {#each shown_balance_other as [currency, num] (currency)}
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
