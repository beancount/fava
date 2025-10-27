<script lang="ts">
  import type { Snippet } from "svelte";

  import { router } from "../router.ts";
  import {
    barChartMode,
    chartToggledCurrencies,
    hierarchyChartMode,
    lineChartMode,
  } from "../stores/chart.ts";
  import { show_charts } from "../stores/url.ts";
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
</script>

<div class="flex-row">
  {#if $show_charts}
    {#if chart.type === "barchart"}
      <ChartLegend
        legend={chart.currencies}
        color={!($barChartMode === "stacked" && chart.hasStackedData)}
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
    {#if chart.type === "hierarchy" && $hierarchyChartMode === "treemap" && chart.treemap_currency}
      <ChartLegend
        legend={chart.currencies}
        color={false}
        active={chart.treemap_currency}
      />
    {/if}
    <span class="spacer"></span>
    {#if chart.type === "hierarchy"}
      <ModeSwitch store={hierarchyChartMode} />
    {:else if chart.type === "linechart"}
      <ModeSwitch store={lineChartMode} />
    {:else if chart.type === "barchart" && chart.hasStackedData}
      <ModeSwitch store={barChartMode} />
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
  @media print {
    button.show-charts {
      display: none;
    }
  }
</style>
