<script lang="ts">
  import { onMount } from "svelte";

  import { bindKey } from "../keyboard-shortcuts";
  import { lastActiveChartName, showCharts } from "../stores/chart";

  import Chart from "./Chart.svelte";
  import ConversionAndInterval from "./ConversionAndInterval.svelte";

  import type { NamedFavaChart } from ".";

  export let charts: NamedFavaChart[];

  const setChart = (c: NamedFavaChart) => {
    $lastActiveChartName = c.name;
  };

  $: active_chart =
    charts.find((c) => c.name === $lastActiveChartName) ?? charts?.[0];

  const nextChart = () => {
    const currentIndex = charts.findIndex((e) => e === active_chart);
    const next = charts[(currentIndex + 1 + charts.length) % charts.length];
    if (next) {
      setChart(next);
    }
  };
  const previousChart = () => {
    const currentIndex = charts.findIndex((e) => e === active_chart);
    const prev = charts[(currentIndex - 1 + charts.length) % charts.length];
    if (prev) {
      setChart(prev);
    }
  };

  onMount(() => bindKey("c", nextChart));
  onMount(() => bindKey("C", previousChart));
</script>

{#if charts.length > 0 && active_chart}
  <Chart chart={active_chart}>
    <ConversionAndInterval />
  </Chart>
  <div hidden={!$showCharts}>
    {#each charts as chart}
      <button
        type="button"
        class:selected={chart === active_chart}
        on:click={() => {
          setChart(chart);
        }}
      >
        {chart.name}
      </button>
    {/each}
  </div>
{/if}

<style>
  div {
    margin-bottom: 1.5em;
    font-size: 1em;
    color: var(--text-color-lightest);
    text-align: center;
  }

  button {
    all: unset;
    padding: 0 0.5em;
    cursor: pointer;
  }

  button + button {
    border-left: 1px solid var(--text-color-lighter);
  }

  button.selected,
  button:hover {
    color: var(--text-color-lighter);
  }
</style>
