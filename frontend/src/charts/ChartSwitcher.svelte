<script lang="ts">
  import { onMount } from "svelte";

  import { bindKey } from "../keyboard-shortcuts";
  import { activeChart, showCharts } from "../stores/chart";

  import Chart from "./Chart.svelte";
  import ConversionAndInterval from "./ConversionAndInterval.svelte";

  import { parseChartData } from ".";
  import type { NamedChartTypes } from ".";

  let charts: NamedChartTypes[] = [];

  onMount(() => {
    charts = parseChartData();
    if (!charts.length) {
      $activeChart = undefined;
    }
    $activeChart =
      charts.find((c) => c.name === ($activeChart || {}).name) || charts[0];

    const unbind = [
      bindKey("c", () => {
        const currentIndex = charts.findIndex((e) => e === $activeChart);
        $activeChart =
          charts[(currentIndex + 1 + charts.length) % charts.length];
      }),
      bindKey("C", () => {
        const currentIndex = charts.findIndex((e) => e === $activeChart);
        $activeChart =
          charts[(currentIndex - 1 + charts.length) % charts.length];
      }),
    ];

    return () => {
      unbind.forEach((u) => u());
    };
  });
</script>

{#if $activeChart}
  <Chart chart={$activeChart}>
    <ConversionAndInterval />
  </Chart>
  <div hidden={!$showCharts}>
    {#each charts as chart}
      <span
        class:selected={chart === $activeChart}
        on:click={() => {
          $activeChart = chart;
        }}
      >
        {chart.name}
      </span>
    {/each}
  </div>
{/if}

<style>
  div {
    margin-bottom: 1.5em;
    font-size: 1em;
    color: var(--color-text-lightest);
    text-align: center;
  }

  span {
    padding: 0 0.5em;
    cursor: pointer;
  }

  span + span {
    border-left: 1px solid var(--color-text-lighter);
  }

  span.selected,
  span:hover {
    color: var(--color-text-lighter);
  }
</style>
