<script lang="ts">
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import { ParsedHierarchyChart } from "../../charts/hierarchy.ts";
  import { get_date_format } from "../../format.ts";
  import { url_for_account } from "../../helpers.ts";
  import { _ } from "../../i18n.ts";
  import { is_non_empty } from "../../lib/array.ts";
  import { interval_label } from "../../lib/interval.ts";
  import { fiscal_year_end } from "../../stores/fava_options.ts";
  import { interval as current_interval } from "../../stores/url.ts";
  import IntervalTreeTable from "../../tree-table/IntervalTreeTable.svelte";
  import JournalTable from "../journal/JournalTable.svelte";
  import type { AccountReportProps } from "./index.ts";

  let { account, report_type, report }: AccountReportProps = $props();

  let accumulate = $derived(report_type === "balances");
  let interval_label_lower = $derived(
    interval_label($current_interval).toLowerCase(),
  );

  let all_charts = $derived.by(() => {
    if (report.type === "journal") {
      return report.charts;
    }
    const { charts, interval_balances, dates, interval } = report;
    const date_format = get_date_format(interval, $fiscal_year_end);
    return [
      ...charts,
      ...interval_balances
        .slice(0, 3)
        .map(
          (node, index) =>
            new ParsedHierarchyChart(
              date_format(dates[index]?.begin ?? new Date()),
              node,
              `interval_${index.toString()}`,
            ),
        ),
    ];
  });
</script>

<ChartSwitcher charts={all_charts} />

<div class="droptarget" data-account-name={account}>
  <div class="headerline">
    <h3>
      {#if report_type !== "journal"}
        <a
          href={$url_for_account(account)}
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
        <a href={$url_for_account(account, { r: "changes" })}>
          {_("Changes")} ({interval_label_lower})
        </a>
      {:else}
        {_("Changes")} ({interval_label_lower})
      {/if}
    </h3>
    <h3>
      {#if report_type !== "balances"}
        <a href={$url_for_account(account, { r: "balances" })}>
          {_("Balances")} ({interval_label_lower})
        </a>
      {:else}
        {_("Balances")} ({interval_label_lower})
      {/if}
    </h3>
  </div>
  {#if report.type === "journal"}
    <JournalTable
      journal={report.journal}
      initial_sort={["date", "desc"]}
      show_change_and_balance={true}
    />
  {:else if is_non_empty(report.interval_balances)}
    <IntervalTreeTable
      trees={report.interval_balances}
      dates={report.dates}
      budgets={report.budgets}
      interval={report.interval}
      {accumulate}
    />
  {/if}
</div>
