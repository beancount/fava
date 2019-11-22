<script>
  import { onMount } from "svelte";

  import { parseChartData } from ".";
  import { activeChart, showCharts } from "../stores/chart";

  import ConversionAndInterval from "./ConversionAndInterval.svelte";
  import Chart from "./Chart.svelte";

  let charts = [];

  onMount(() => {
    charts = parseChartData();
    if (charts.length) {
      $activeChart =
        charts.find(c => c.name === $activeChart.name) || charts[0];
    }
  });
</script>

{#if charts.length}
  <Chart chart={$activeChart}>
    <ConversionAndInterval />
  </Chart>
  <div hidden={!$showCharts} class="chart-labels">
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
