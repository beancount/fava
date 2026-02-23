<script lang="ts">
  import { getUrlPath } from "../helpers.ts";
  import { _ } from "../i18n.ts";
  import type { KeySpec } from "../keyboard-shortcuts.ts";
  import { keyboardShortcut } from "../keyboard-shortcuts.ts";
  import { router } from "../router.ts";
  import { lastActiveChartPerReport } from "../stores/chart.ts";
  import { current_url, show_charts, url_chart } from "../stores/url.ts";
  import Chart from "./Chart.svelte";
  import { chartContext } from "./context.ts";
  import ConversionAndInterval from "./ConversionAndInterval.svelte";
  import type { ParsedFavaChart } from "./index.ts";

  interface Props {
    charts: readonly ParsedFavaChart[];
  }

  let { charts }: Props = $props();

  // Extract the report name from the current URL (e.g., "balance_sheet" from "/ledger/balance_sheet/")
  let report_name = $derived.by(() => {
    const path = getUrlPath($current_url);
    if (path.is_ok) {
      // Path is like "balance_sheet/" - extract the report name
      const match = /^([^/]+)/.exec(path.value);
      return match ? match[1] : null;
    }
    return null;
  });

  // Get the stored chart name for this report
  let stored_chart_name = $derived(
    report_name != null ? lastActiveChartPerReport.get(report_name) : undefined,
  );

  // Prefer URL chart parameter if set, otherwise fall back to stored chart for this report
  let active_chart = $derived(
    charts.find((c) => c.label === $url_chart) ??
      charts.find((c) => c.label === stored_chart_name) ??
      charts[0],
  );

  // Sync active chart to URL when it doesn't match (e.g., on page load)
  $effect(() => {
    const label = active_chart?.label;
    if (label != null && label !== $url_chart) {
      router.set_search_param("chart", label);
    }
  });

  // Get the shortcut key for jumping to the previous chart.
  let shortcutPrevious = $derived((index: number): KeySpec | undefined => {
    const current = active_chart ? charts.indexOf(active_chart) : -1;
    return index === (current - 1 + charts.length) % charts.length
      ? { key: "C", note: _("Previous") }
      : undefined;
  });
  // Get the shortcut key for jumping to the next chart.
  let shortcutNext = $derived((index: number): KeySpec | undefined => {
    const current = active_chart ? charts.indexOf(active_chart) : -1;
    return index === (current + 1 + charts.length) % charts.length
      ? { key: "c", note: _("Next") }
      : undefined;
  });
</script>

{#if active_chart}
  <Chart chart={active_chart.with_context($chartContext)}>
    <ConversionAndInterval />
  </Chart>
  <div hidden={!$show_charts}>
    {#each charts as chart, index (chart.label)}
      <button
        type="button"
        class="unset"
        class:selected={chart === active_chart}
        onclick={() => {
          const label = chart.label;
          if (label == null) {
            return;
          }
          const currentReport = report_name;
          if (currentReport != null) {
            lastActiveChartPerReport.set(currentReport, label);
          }
          router.set_search_param("chart", label);
        }}
        {@attach keyboardShortcut(shortcutPrevious(index))}
        {@attach keyboardShortcut(shortcutNext(index))}
      >
        {chart.label}
      </button>
    {/each}
  </div>
{/if}

<style>
  div {
    margin-bottom: 1em;
    color: var(--text-color-lightest);
    text-align: center;
  }

  button {
    padding: 0 0.5em;
  }

  button + button {
    border-left: 1px solid var(--text-color-lighter);
  }

  button.selected,
  button:hover {
    color: var(--text-color-lighter);
  }

  @media print {
    button {
      display: none;
      border-left: none;
    }

    button + button {
      border-left: none;
    }

    button.selected {
      display: inline;
    }
  }
</style>
