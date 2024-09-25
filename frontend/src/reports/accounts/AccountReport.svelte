<script lang="ts">
  import type { AccountBudget } from "../../api/validators";
  import { parseChartData } from "../../charts";
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import { chartContext } from "../../charts/context";
  import type { AccountTreeNode } from "../../charts/hierarchy";
  import { urlForAccount } from "../../helpers";
  import { _ } from "../../i18n";
  import { is_non_empty } from "../../lib/array";
  import { intervalLabel } from "../../lib/interval";
  import { interval } from "../../stores";
  import IntervalTreeTable from "../../tree-table/IntervalTreeTable.svelte";
  import type { AccountReportType } from ".";

  export let account: string;
  export let report_type: AccountReportType;
  export let charts: unknown;
  export let journal: string | null;
  export let interval_balances: AccountTreeNode[] | null;
  export let dates: { begin: Date; end: Date }[] | null;
  export let budgets: Record<string, AccountBudget[]> | null;

  $: accumulate = report_type === "balances";

  $: chartData = parseChartData(charts, $chartContext).unwrap_or(null);
  $: interval_label = intervalLabel($interval).toLowerCase();
</script>

{#if chartData}
  <ChartSwitcher charts={chartData} />
{/if}

<div class="droptarget" data-account-name={account}>
  <div class="headerline">
    <h3>
      {#if report_type !== "journal"}
        <a
          href={$urlForAccount(account)}
          title={_("Journal of all entries for this Account and Sub-Accounts")}
        >
          {_("Account Journal")}
        </a>
      {:else}
        {_("Account Journal")}
      {/if}
    </h3>
    <h3>
      {#if report_type !== "changes"}
        <a href={$urlForAccount(account, { r: "changes" })}>
          {_("Changes")} ({interval_label})
        </a>
      {:else}
        {_("Changes")} ({interval_label})
      {/if}
    </h3>
    <h3>
      {#if report_type !== "balances"}
        <a href={$urlForAccount(account, { r: "balances" })}>
          {_("Balances")} ({interval_label})
        </a>
      {:else}
        {_("Balances")} ({interval_label})
      {/if}
    </h3>
  </div>
  {#if report_type === "journal"}
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    {@html journal}
  {:else if interval_balances && is_non_empty(interval_balances) && budgets && dates}
    <IntervalTreeTable
      trees={interval_balances}
      {dates}
      {budgets}
      {accumulate}
    />
  {/if}
</div>
