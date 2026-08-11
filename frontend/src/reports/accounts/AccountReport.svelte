<script lang="ts">
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import { ParsedHierarchyChart } from "../../charts/hierarchy.ts";
  import type { ParsedFavaChart } from "../../charts/index.ts";
  import { urlForAccount } from "../../helpers.ts";
  import { _ } from "../../i18n.ts";
  import { is_non_empty } from "../../lib/array.ts";
  import { intervalLabel } from "../../lib/interval.ts";
  import { router } from "../../router.ts";
  import { lastActiveChartName } from "../../stores/chart.ts";
  import { currentTimeFilterDateFormat } from "../../stores/format.ts";
  import { interval } from "../../stores/url.ts";
  import IntervalTreeTable from "../../tree-table/IntervalTreeTable.svelte";
  import JournalTable from "../journal/JournalTable.svelte";
  import type { AccountReportProps } from "./index.ts";

  let {
    account,
    report_type,
    initial_chart_index,
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

  const to_chart_name = (s: string | null, charts: ParsedFavaChart[]): string =>
    charts[parseInt(s ?? "0", 10)]?.label ?? charts[0]?.label ?? "";

  // On load, set the selected chart from the URL
  $effect(() => {
    lastActiveChartName.set(to_chart_name(initial_chart_index, all_charts));
  });

  // Derive the index from the chart name for the URL building
  let chart_index: string = $derived.by(() => {
    const idx = all_charts.findIndex((c) => c.label === $lastActiveChartName);
    return idx <= 0 ? "0" : String(idx);
  });

  // On chart change, write selected chart index to the URL
  $effect(() => {
    const target = new URL(router.current);
    if (chart_index === "0") {
      target.searchParams.delete("c");
    } else {
      target.searchParams.set("c", chart_index);
    }
    if (target.href !== router.current.href) {
      router.navigate(target, false);
    }
  });
</script>

<ChartSwitcher charts={all_charts} />

<div class="droptarget" data-account-name={account}>
  <div class="headerline">
    <h3>
      {#if report_type !== "journal"}
        <a
          href={$urlForAccount(account, { c: chart_index })}
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
        <a href={$urlForAccount(account, { r: "changes", c: chart_index })}>
          {_("Changes")} ({interval_label})
        </a>
      {:else}
        {_("Changes")} ({interval_label})
      {/if}
    </h3>
    <h3>
      {#if report_type !== "balances"}
        <a href={$urlForAccount(account, { r: "balances", c: chart_index })}>
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
