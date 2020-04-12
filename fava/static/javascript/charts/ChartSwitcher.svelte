<script>
  import { onDestroy, onMount } from "svelte";

  import { keys } from "../keyboard-shortcuts";
  import { parseChartData } from ".";
  import { activeChart, showCharts } from "../stores/chart";

  import ConversionAndInterval from "./ConversionAndInterval.svelte";
  import Chart from "./Chart.svelte";

  let charts = [];

  onMount(() => {
    charts = parseChartData();
    if (!charts.length) {
      return;
    }
    $activeChart =
      charts.find((c) => c.name === $activeChart.name) || charts[0];
    keys.bind("c", () => {
      const currentIndex = charts.findIndex((e) => e === $activeChart);
      $activeChart = charts[(currentIndex + 1 + charts.length) % charts.length];
    });
    keys.bind("C", () => {
      const currentIndex = charts.findIndex((e) => e === $activeChart);
      $activeChart = charts[(currentIndex - 1 + charts.length) % charts.length];
    });
  });
  onDestroy(() => {
    keys.unbind("c");
    keys.unbind("C");
  });
</script>

<style>
  div {
    margin-bottom: 1.5em;
    font-size: 1em;
    color: var(--color-text-lightest);
    text-align: center;
  }

  label {
    padding: 0 0.5em;
  }

  label + label {
    border-left: 1px solid var(--color-text-lighter);
  }

  label.selected,
  label:hover {
    color: var(--color-text-lighter);
  }
</style>

{#if charts.length}
  <Chart chart={$activeChart}>
    <ConversionAndInterval />
  </Chart>
  <div hidden={!$showCharts}>
    {#each charts as chart}
      <label
        class:selected={chart === $activeChart}
        on:click={() => {
          $activeChart = chart;
        }}>
        {chart.name}
      </label>
    {/each}
  </div>
{/if}
