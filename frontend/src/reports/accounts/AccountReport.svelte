<script lang="ts">
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import { ParsedHierarchyChart } from "../../charts/hierarchy.ts";
  import { urlForAccount } from "../../helpers.ts";
  import { _ } from "../../i18n.ts";
  import { is_non_empty } from "../../lib/array.ts";
  import { intervalLabel } from "../../lib/interval.ts";
  import { currentTimeFilterDateFormat } from "../../stores/format.ts";
  import { interval } from "../../stores/url.ts";
  import IntervalTreeTable from "../../tree-table/IntervalTreeTable.svelte";
  import JournalTable from "../journal/JournalTable.svelte";
  import type { AccountReportProps } from "./index.ts";

  let {
    account,
    report_type,
    charts,
    journal,
    interval_balances,
    dates,
    budgets,
  }: AccountReportProps = $props();

  let accumulate = $derived(report_type === "balances");
  let interval_label = $derived(intervalLabel($interval).toLowerCase());

  let all_charts = $derived(
    interval_balances && dates
      ? [
          ...charts,
          ...interval_balances
            .slice(0, 3)
            .map(
              (node, index) =>
                new ParsedHierarchyChart(
                  $currentTimeFilterDateFormat(
                    dates[index]?.begin ?? new Date(),
                  ),
                  node,
                ),
            ),
        ]
      : charts,
  );
</script>

<ChartSwitcher charts={all_charts} />

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
  {#if report_type === "journal" && journal != null}
    <JournalTable
      {journal}
      initial_sort={["date", "desc"]}
      show_change_and_balance={true}
    />
  {:else if interval_balances && is_non_empty(interval_balances) && budgets && dates}
    <IntervalTreeTable
      trees={interval_balances}
      {dates}
      {budgets}
      {accumulate}
    />
  {/if}
</div>
