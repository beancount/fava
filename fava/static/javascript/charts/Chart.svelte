<script>
  import { tick } from "svelte";

  import { _ } from "../helpers";
  import { chartCurrency, chartMode, showCharts } from "../stores/chart";

  export let chart;
  let svg;

  let renderedChart;
  let hasCurrencySetting;
  let chartWidth;

  async function chartChanged() {
    await tick();
    if (!svg) {
      return;
    }
    renderedChart = chart
      .renderer(svg)
      .setWidth(chartWidth)
      .set("mode", $chartMode)
      .set("currency", $chartCurrency)
      .draw(chart.data);
    hasCurrencySetting = renderedChart.has_currency_setting;
  }
  $: if (chart) {
    chartChanged();
  }

  $: if (renderedChart) {
    renderedChart
      .setWidth(chartWidth)
      .set("mode", $chartMode)
      .set("currency", $chartCurrency)
      .update();
    hasCurrencySetting = renderedChart.has_currency_setting;
  }

  $: legend = (renderedChart && renderedChart.legend) || { domain: [] };
  $: currencies = (renderedChart && renderedChart.currencies) || [];
  $: hasModeSetting = renderedChart && renderedChart.has_mode_setting;
</script>

<form class="wide-form">
  <p hidden={!$showCharts} class="chart-legend">
    {#each legend.domain.sort() as item}
      <span class="legend">
        <i class="color" style="background-color: {legend.scale(item)}" />
        {item}
      </span>
    {/each}
  </p>
  <span class="spacer" />
  <select
    bind:value={$chartCurrency}
    hidden={!$showCharts || !hasCurrencySetting}>
    {#each currencies as currency}
      <option value={currency}>{currency}</option>
    {/each}
  </select>
  <span hidden={!$showCharts || !hasModeSetting} class="chart-mode">
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
    data-key="ctrl+c"
    class:closed={!$showCharts}
    class="toggle-chart" />
</form>
<div hidden={!$showCharts} bind:clientWidth={chartWidth}>
  <svg bind:this={svg} />
</div>
