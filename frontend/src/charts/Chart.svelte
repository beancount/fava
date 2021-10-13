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
  import ModeSwitch from "./ModeSwitch.svelte";
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
      <ModeSwitch
        bind:value={$hierarchyChartMode}
        options={[
          ["treemap", _("Treemap")],
          ["sunburst", _("Sunburst")],
        ]}
      />
    {:else if chart.type === "linechart"}
      <ModeSwitch
        bind:value={$lineChartMode}
        options={[
          ["line", _("Line chart")],
          ["area", _("Area chart")],
        ]}
      />
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

<style>
  .toggle-chart {
    height: 22px;
    padding: 2px 6px;
    margin: 0;
  }

  .toggle-chart::before {
    display: block;
    content: "";
    border: 0;
    border-top: 13px solid var(--background);
    border-right: 9px solid transparent;
    border-left: 9px solid transparent;
  }

  .toggle-chart.closed::before {
    border: 0;
    border-right: 9px solid transparent;
    border-bottom: 13px solid var(--background);
    border-left: 9px solid transparent;
  }
</style>
