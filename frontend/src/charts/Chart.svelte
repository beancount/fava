<script lang="ts">
  import type { Snippet } from "svelte";

  import {
    barChartMode,
    chartToggledCurrencies,
    hierarchyChartMode,
    lineChartMode,
    showCharts,
  } from "../stores/chart";
  import type { FavaChart } from ".";
  import BarChart from "./BarChart.svelte";
  import ChartLegend from "./ChartLegend.svelte";
  import HierarchyContainer from "./HierarchyContainer.svelte";
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
  {#if $showCharts}
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
      showCharts.update((v) => !v);
    }}
  >
    {$showCharts ? "▼" : "◀"}
  </button>
</div>
<div hidden={!$showCharts} bind:clientWidth={width}>
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
