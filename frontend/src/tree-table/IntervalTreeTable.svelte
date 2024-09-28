<script lang="ts">
  import { intersection, min } from "d3-array";
  import { writable } from "svelte/store";

  import type { AccountBudget } from "../api/validators";
  import type { AccountTreeNode } from "../charts/hierarchy";
  import { urlForAccount } from "../helpers";
  import type { NonEmptyArray } from "../lib/array";
  import { collapse_account } from "../stores/accounts";
  import { currentTimeFilterDateFormat } from "../stores/format";
  import AccountCellHeader from "./AccountCellHeader.svelte";
  import { get_collapsed, get_not_shown, setTreeTableContext } from "./helpers";
  import IntervalTreeTableNode from "./IntervalTreeTableNode.svelte";

  /** The account trees to show. */
  export let trees: NonEmptyArray<AccountTreeNode>;
  /** The dates. */
  export let dates: { begin: Date; end: Date }[];
  /** The budgets (per account a list per date range). */
  export let budgets: Record<string, AccountBudget[]>;
  /** Whether this is cumulative. */
  export let accumulate: boolean;

  // Initialize context.
  // toggled is computed once on initialisation; not_shown is kept updated.
  const toggled = writable(get_collapsed(trees[0], $collapse_account));
  const not_shown = writable(new Set<string>());
  setTreeTableContext({ toggled, not_shown });
  $: $not_shown = intersection(
    ...trees.map((n, index) => $get_not_shown(n, dates[index]?.end ?? null)),
  );

  $: account = trees[0].account;
  $: start_date = accumulate ? min(dates, (d) => d.begin) : undefined;
  $: start_date_filter = start_date
    ? $currentTimeFilterDateFormat(start_date)
    : undefined;
  $: time_filters = dates.map((date_range): [string, string] => {
    const title = $currentTimeFilterDateFormat(date_range.begin);
    return start_date_filter != null
      ? [title, `${start_date_filter}-${title}`]
      : [title, title];
  });
</script>

<ol class="flex-table tree-table-new">
  <li class="head">
    <p>
      <AccountCellHeader />
      {#each time_filters as [title, time]}
        <span class="num other">
          <a href={$urlForAccount(account, { time })}>
            {title}
          </a>
        </span>
      {/each}
    </p>
  </li>
  <IntervalTreeTableNode nodes={trees} {budgets} />
</ol>

<style>
  ol {
    overflow-x: auto;
  }
</style>
