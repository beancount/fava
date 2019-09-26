<script>
  import { onMount, tick } from "svelte";

  import { _ } from "./helpers";
  import { parseChartData } from "./charts";
  import {
    favaAPI,
    activeChart,
    chartCurrency,
    chartMode,
    conversion,
    interval,
    showCharts,
  } from "./stores";

  let charts = [];
  let svg;

  let renderedChart;
  let chart;
  let hasCurrencySetting;
  let chartWidth;

  const conversions = [
    ["at_cost", _("At Cost")],
    ["at_value", _("At Market Value")],
    ["units", _("Units")],
    ...favaAPI.options.operating_currency
      .sort()
      .map(currency => [currency, `Converted to ${currency}`]),
    ...favaAPI.options.commodities
      .sort()
      .filter(
        c => !favaAPI.options.operating_currency.includes(c) && c.length <= 3
      )
      .map(currency => [currency, `Converted to ${currency}`]),
  ];
  // TODO  _('Converted to %(currency)s', currency=currency)

  async function selectChart(index) {
    chart = charts[index];
    $activeChart = {
      name: chart.name,
      index,
    };
    await tick();
    renderedChart = chart
      .renderer(svg)
      .setWidth(chartWidth)
      .set("mode", $chartMode)
      .set("currency", $chartCurrency)
      .draw(chart.data);
    hasCurrencySetting = renderedChart.has_currency_setting;
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

  onMount(() => {
    charts = parseChartData();
    if (charts.length) {
      const active = charts[$activeChart.index];
      if (active && active.name === $activeChart.name) {
        selectChart($activeChart.index);
      } else {
        selectChart(0);
      }
    }
  });

  const intervals = {
    year: _("Yearly"),
    quarter: _("Quarterly"),
    month: _("Monthly"),
    week: _("Weekly"),
    day: _("Daily"),
  };
</script>

{#if charts.length}
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
    <select bind:value={$conversion}>
      {#each conversions as [conversion, conversionName]}
        <option value={conversion}>{conversionName}</option>
      {/each}
    </select>
    <select bind:value={$interval}>
      {#each Object.keys(intervals) as key}
        <option value={key}>{intervals[key]}</option>
      {/each}
    </select>
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
  <div hidden={!$showCharts} class="chart-labels">
    {#each charts as chart, index}
      <label
        class:selected={index === $activeChart.index}
        on:click={() => selectChart(index)}>
        {chart.name}
      </label>
    {/each}
  </div>
{/if}
