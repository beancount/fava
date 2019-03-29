<script>
  import { onMount, tick } from "svelte";

  import { select } from "d3-selection";
  import { _ } from "./helpers";
  import router from "./router";
  import { parseChartData } from "./charts";
  import {
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
    ...window.favaAPI.options.operating_currency
      .sort()
      .map(currency => [currency, `Converted to ${currency}`]),
    ...window.favaAPI.options.commodities
      .sort()
      .filter(
        c =>
          !window.favaAPI.options.operating_currency.includes(c) &&
          c.length <= 3
      )
      .map(currency => [currency, `Converted to ${currency}`]),
  ];
  // TODO  _('Converted to %(currency)s', currency=currency)

  $: if ($chartCurrency || $chartMode || chartWidth || true) {
    update();
  }

  $: legend = (renderedChart && renderedChart.legend) || {};
  $: currencies = (renderedChart && renderedChart.currencies) || [];
  $: hasModeSetting = renderedChart && renderedChart.has_mode_setting;

  onMount(() => {
    const chartData = JSON.parse(
      document.querySelector("#chart-data").innerHTML
    );
    charts = parseChartData(chartData, $conversion, $interval);
    if (charts.length) {
      const chart = charts[$activeChart.index];
      if (chart && chart.name == $activeChart.name) {
        selectChart($activeChart.index);
      } else {
        selectChart(0);
      }
    }
  });

  async function selectChart(index) {
    chart = charts[index];
    $activeChart = {
      name: chart.name,
      index,
    };
    await tick();
    renderedChart = chart
      .renderer(select(svg))
      .setWidth(chartWidth)
      .set("mode", $chartMode)
      .set("currency", $chartCurrency)
      .draw(chart.data);
    hasCurrencySetting = renderedChart.has_currency_setting;
  }

  function update() {
    if (!renderedChart) return;
    renderedChart
      .setWidth(chartWidth)
      .set("mode", $chartMode)
      .set("currency", $chartCurrency)
      .update();
    hasCurrencySetting = renderedChart.has_currency_setting;
  }

  const intervals = {
    year: _("Yearly"),
    quarter: _("Quarterly"),
    month: _("Monthly"),
    week: _("Weekly"),
    day: _("Daily"),
  };
</script>
<svelte:window on:resize="{update}" />
{#if charts.length}
<div class="charts" class:hide-charts="{!$showCharts}">
  <form class="wide-form">
    <span class:hidden="{!$showCharts}" class="chart-legend">
      {#if legend.domain} {#each legend.domain.sort() as item}
      <span class="legend">
        <span
          class="color"
          style="background-color: {legend.scale(item)}"
        ></span>
        <span class="name">{item}</span>
      </span>
      {/each} {/if}
    </span>
    <span class="spacer"></span>
    <select
      bind:value="{$chartCurrency}"
      class:hidden="{!$showCharts || !hasCurrencySetting}"
    >
      {#each currencies as currency}
      <option value="{currency}">{currency}</option>
      {/each}
    </select>
    <span class:hidden="{!$showCharts || !hasModeSetting}" class="chart-mode">
      <label>
        <input type="radio" bind:group="{$chartMode}" value="treemap" />
        <span class="button">{_('Treemap')}</span>
      </label>
      <label>
        <input type="radio" bind:group="{$chartMode}" value="sunburst" />
        <span class="button">{_('Sunburst')}</span>
      </label>
    </span>
    <select bind:value="{$conversion}">
      {#each conversions as [conversion, conversionName]}
      <option value="{conversion}">{conversionName}</option>
      {/each}
    </select>
    <select bind:value="{$interval}">
      {#each Object.keys(intervals) as key}
      <option value="{key}">{intervals[key]}</option>
      {/each}
    </select>
    <button
      type="button"
      on:click="{() => {showCharts.update(v => !v)}}"
      data-key="ctrl+c"
      class="toggle-chart"
    ></button>
  </form>
  <div class:hidden="{!$showCharts}" bind:clientWidth="{chartWidth}">
    <svg bind:this="{svg}"></svg>
  </div>
  <div class:hidden="{!$showCharts}" class="chart-labels">
    {#each charts as chart, index}
    <label
      class:selected="{index === $activeChart.index}"
      on:click="{() => selectChart(index)}"
      >{chart.name}</label
    >
    {/each}
  </div>
</div>
{/if}
