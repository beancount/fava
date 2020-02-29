<script>
  import { setContext } from "svelte";
  import { writable } from "svelte/store";

  import { _ } from "../helpers";
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import { chartCurrency, chartMode, showCharts } from "../stores/chart";

  import BarChart from "./BarChart.svelte";
  import HierarchyContainer from "./HierarchyContainer.svelte";
  import LineChart from "./LineChart.svelte";
  import ScatterPlot from "./ScatterPlot.svelte";

  export let chart;

  $: hasCurrencySetting =
    chart.type === "hierarchy" && $chartMode === "treemap";
  let chartWidth = 0;

  const currencies = writable([]);
  const legend = writable({ domain: [] });
  setContext("chart", {
    currencies,
    legend,
  });

  $: if (chart) {
    legend.set({ domain: [] });
  }
</script>

<form class="wide-form">
  <p hidden={!$showCharts} class="chart-legend">
    {#each $legend.domain.sort() as item}
      <span class="legend">
        <i class="color" style="background-color: {$legend.scale(item)}" />
        {item}
      </span>
    {/each}
  </p>
  <span class="spacer" />
  <select
    bind:value={$chartCurrency}
    hidden={!$showCharts || !hasCurrencySetting}>
    {#each $currencies as currency}
      <option value={currency}>{currency}</option>
    {/each}
  </select>
  <span hidden={!$showCharts || chart.type !== 'hierarchy'} class="chart-mode">
    <label>
      <input type="radio" bind:group={$chartMode} value="treemap" />
      <span class="button">{_('Treemap')}</span>
    </label>
    <label>
      <input type="radio" bind:group={$chartMode} value="sunburst" />
      <span class="button">{_('Sunburst')}</span>
    </label>
  </span>
  <slot />
  <button
    type="button"
    on:click={() => {
      showCharts.update(v => !v);
    }}
    use:keyboardShortcut={'Control+c'}
    class:closed={!$showCharts}
    class="toggle-chart" />
</form>
<div hidden={!$showCharts} bind:clientWidth={chartWidth}>
  {#if chart.type === 'scatterplot'}
    <ScatterPlot data={chart.data} width={chartWidth} />
  {:else if chart.type === 'barchart'}
    <BarChart
      data={chart.data}
      width={chartWidth}
      tooltipText={chart.tooltipText} />
  {:else if chart.type === 'linechart'}
    <LineChart
      data={chart.data}
      width={chartWidth}
      tooltipText={chart.tooltipText} />
  {:else}
    <HierarchyContainer data={chart.data} width={chartWidth} />
  {/if}
</div>
