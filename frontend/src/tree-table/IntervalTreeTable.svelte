<script lang="ts">
  import { intersection, min } from "d3-array";
  import { writable } from "svelte/store";

  import type { AccountBudget } from "../api/validators";
  import type { AccountTreeNode } from "../charts/hierarchy";
  import { urlForAccount } from "../helpers";
  import type { NonEmptyArray } from "../lib/array";
  import { currentTimeFilterDateFormat } from "../stores/format";
  import AccountCellHeader from "./AccountCellHeader.svelte";
  import { get_not_shown, setTreeTableNotShownContext } from "./helpers";
  import IntervalTreeTableNode from "./IntervalTreeTableNode.svelte";

  interface Props {
    /** The account trees to show. */
    trees: NonEmptyArray<AccountTreeNode>;
    /** The dates. */
    dates: { begin: Date; end: Date }[];
    /** The budgets (per account a list per date range). */
    budgets: Record<string, AccountBudget[]>;
    /** Whether this is cumulative. */
    accumulate: boolean;
  }

  let { trees, dates, budgets, accumulate }: Props = $props();

  const not_shown = writable(new Set<string>());
  setTreeTableNotShownContext(not_shown);

  $effect(() => {
    $not_shown = intersection(
      ...trees.map((n, index) => $get_not_shown(n, dates[index]?.end ?? null)),
    );
  });

  let account = $derived(trees[0].account);
  let start_date = $derived(
    accumulate ? min(dates, (d) => d.begin) : undefined,
  );
  let start_date_filter = $derived(
    start_date ? $currentTimeFilterDateFormat(start_date) : undefined,
  );
  let time_filters = $derived(
    dates.map((date_range): [string, string] => {
      const title = $currentTimeFilterDateFormat(date_range.begin);
      return start_date_filter != null
        ? [title, `${start_date_filter}-${title}`]
        : [title, title];
    }),
  );
</script>

<ol class="flex-table tree-table-new">
  <li class="head">
    <p>
      <AccountCellHeader {account} />
      {#each time_filters as [title, time] (time)}
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
