<script lang="ts">
  import { setContext } from "svelte";
  import { writable } from "svelte/store";
  import type { Writable } from "svelte/store";

  import { _ } from "../i18n";
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import {
    chartCurrency,
    hierarchyChartMode,
    lineChartMode,
    showCharts,
  } from "../stores/chart";

  import BarChart from "./BarChart.svelte";
  import ChartLegend from "./ChartLegend.svelte";
  import HierarchyContainer from "./HierarchyContainer.svelte";
  import LineChart from "./LineChart.svelte";
  import ScatterPlot from "./ScatterPlot.svelte";

  import type { NamedChartTypes } from ".";

  /**
   * The chart to render.
   */
  export let chart: NamedChartTypes;

  /**
   * Width of the chart.
   */
  let width: number;

  const currencies: Writable<string[]> = writable([]);
  setContext("chart-currencies", currencies);

  const legend: Writable<[string, string][]> = writable([]);
  setContext("chart-legend", legend);

  $: if (chart) {
    // Reset the chart legend on chart change.
    legend.set([]);
  }

  const components = {
    barchart: BarChart,
    hierarchy: HierarchyContainer,
    linechart: LineChart,
    scatterplot: ScatterPlot,
  };
</script>

<div class="flex-row">
  {#if $showCharts}
    <div>
      <ChartLegend legend={$legend} />
    </div>
    <span class="spacer" />
    {#if chart.type === "hierarchy"}
      {#if $hierarchyChartMode === "treemap"}
        <select bind:value={$chartCurrency}>
          {#each $currencies as currency}
            <option value={currency}>{currency}</option>
          {/each}
        </select>
      {/if}
      <span class="chart-mode">
        <label>
          <input
            type="radio"
            bind:group={$hierarchyChartMode}
            value="treemap"
          />
          <span class="button">{_("Treemap")}</span>
        </label>
        <label>
          <input
            type="radio"
            bind:group={$hierarchyChartMode}
            value="sunburst"
          />
          <span class="button">{_("Sunburst")}</span>
        </label>
      </span>
    {:else if chart.type === "linechart"}
      <span class="chart-mode">
        <label>
          <input type="radio" bind:group={$lineChartMode} value="line" />
          <span class="button">{_("Line chart")}</span>
        </label>
        <label>
          <input type="radio" bind:group={$lineChartMode} value="area" />
          <span class="button">{_("Area chart")}</span>
        </label>
      </span>
    {/if}
  {:else}<span class="spacer" />{/if}
  <slot />
  <button
    type="button"
    on:click={() => showCharts.update((v) => !v)}
    use:keyboardShortcut={"Control+c"}
    class:closed={!$showCharts}
    class="toggle-chart"
  />
</div>
<div hidden={!$showCharts} bind:clientWidth={width}>
  {#if width}
    {#if components[chart.type]}
      <svelte:component
        this={components[chart.type]}
        data={chart.data}
        tooltipText={chart.tooltipText}
        {width}
      />
    {:else}Invalid chart: {chart.type}{/if}
  {/if}
</div>
