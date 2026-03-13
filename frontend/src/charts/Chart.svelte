<script lang="ts">
  import type { Snippet } from "svelte";

  import { getUrlPath } from "../helpers.ts";
  import { router } from "../router.ts";
  import {
    barChartMode,
    chartToggledCurrencies,
    hierarchyChartMode,
    lastActiveChartModePerReport,
    lineChartMode,
  } from "../stores/chart.ts";
  import { current_url, show_charts, url_chart_mode } from "../stores/url.ts";
  import BarChart from "./BarChart.svelte";
  import ChartLegend from "./ChartLegend.svelte";
  import HierarchyContainer from "./HierarchyContainer.svelte";
  import type { FavaChart } from "./index.ts";
  import LineChart from "./LineChart.svelte";
  import ModeSwitch from "./ModeSwitch.svelte";
  import ScatterPlot from "./ScatterPlot.svelte";

  interface Props {
    /** The chart to render. */
    chart: FavaChart;
    /** Additional elements to render in the top right. */
    children?: Snippet;
  }

  let { chart, children }: Props = $props();

  /** Width of the chart. */
  let width: number | undefined = $state();

  // Extract the report name from the current URL
  let report_name = $derived.by(() => {
    const path = getUrlPath($current_url);
    if (path.is_ok) {
      const match = /^([^/]+)/.exec(path.value);
      return match ? match[1] : null;
    }
    return null;
  });

  // Get the stored chart mode for this report (falls back to global store default)
  let stored_chart_mode = $derived(
    report_name != null
      ? lastActiveChartModePerReport.get(report_name)
      : undefined,
  );

  // Derive effective modes: URL > per-report storage > global store
  const valid_hierarchy_modes = ["treemap", "sunburst", "icicle"];
  const valid_bar_modes = ["stacked", "single"];
  const valid_line_modes = ["line", "area"];

  let effective_hierarchy_mode = $derived.by(() => {
    if (
      $url_chart_mode != null &&
      valid_hierarchy_modes.includes($url_chart_mode)
    ) {
      return $url_chart_mode;
    }
    if (
      stored_chart_mode != null &&
      valid_hierarchy_modes.includes(stored_chart_mode)
    ) {
      return stored_chart_mode;
    }
    return $hierarchyChartMode;
  });

  let effective_bar_mode = $derived.by(() => {
    if ($url_chart_mode != null && valid_bar_modes.includes($url_chart_mode)) {
      return $url_chart_mode;
    }
    if (
      stored_chart_mode != null &&
      valid_bar_modes.includes(stored_chart_mode)
    ) {
      return stored_chart_mode;
    }
    return $barChartMode;
  });

  let effective_line_mode = $derived.by(() => {
    if ($url_chart_mode != null && valid_line_modes.includes($url_chart_mode)) {
      return $url_chart_mode;
    }
    if (
      stored_chart_mode != null &&
      valid_line_modes.includes(stored_chart_mode)
    ) {
      return stored_chart_mode;
    }
    return $lineChartMode;
  });

  // Determine the current effective mode based on chart type
  let current_effective_mode = $derived.by(() => {
    if (chart.type === "hierarchy") {
      return effective_hierarchy_mode;
    } else if (chart.type === "barchart" && chart.hasStackedData) {
      return effective_bar_mode;
    } else if (chart.type === "linechart") {
      return effective_line_mode;
    }
    return null;
  });

  // Sync effective mode to URL when it doesn't match (e.g., on page load)
  $effect(() => {
    if (
      current_effective_mode != null &&
      current_effective_mode !== $url_chart_mode
    ) {
      router.set_search_param("chart_mode", current_effective_mode);
    }
  });

  /** Update the URL chart_mode parameter and save per-report. */
  function set_chart_mode(value: string): void {
    if (report_name != null) {
      lastActiveChartModePerReport.set(report_name, value);
    }
    router.set_search_param("chart_mode", value);
  }
</script>

<div class="flex-row">
  {#if $show_charts}
    {#if chart.type === "barchart"}
      <ChartLegend
        legend={chart.currencies}
        color={!(effective_bar_mode === "stacked" && chart.hasStackedData)}
        toggled={chartToggledCurrencies}
      />
    {/if}
    {#if chart.type === "linechart"}
      <ChartLegend
        legend={chart.series_names}
        color={true}
        toggled={chartToggledCurrencies}
      />
    {/if}
    {#if chart.type === "hierarchy" && effective_hierarchy_mode === "treemap" && chart.treemap_currency}
      <ChartLegend
        legend={chart.currencies}
        color={false}
        active={chart.treemap_currency}
      />
    {/if}
    <span class="spacer"></span>
    {#if chart.type === "hierarchy"}
      <ModeSwitch
        store={hierarchyChartMode}
        url_value={$url_chart_mode}
        onchange={set_chart_mode}
      />
    {:else if chart.type === "linechart"}
      <ModeSwitch
        store={lineChartMode}
        url_value={$url_chart_mode}
        onchange={set_chart_mode}
      />
    {:else if chart.type === "barchart" && chart.hasStackedData}
      <ModeSwitch
        store={barChartMode}
        url_value={$url_chart_mode}
        onchange={set_chart_mode}
      />
    {/if}
  {:else}<span class="spacer"></span>{/if}
  {@render children?.()}
  <button
    type="button"
    class="show-charts"
    onclick={() => {
      router.set_search_param("charts", $show_charts ? "false" : "");
    }}
  >
    {$show_charts ? "▼" : "◀"}
  </button>
</div>
<div hidden={!$show_charts} bind:clientWidth={width}>
  {#if width}
    {#if chart.type === "barchart"}
      <BarChart {chart} {width} />
    {:else if chart.type === "hierarchy"}
      <HierarchyContainer {chart} {width} />
    {:else if chart.type === "linechart"}
      <LineChart {chart} {width} />
    {:else if chart.type === "scatterplot"}
      <ScatterPlot {chart} {width} />
    {/if}
  {/if}
</div>

<style>
  .flex-row {
    margin-bottom: var(--flex-gap);
  }

  @media print {
    button.show-charts {
      display: none;
    }
  }
</style>
