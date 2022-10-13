<script lang="ts">
  import { onMount } from "svelte";

  import { bindKey } from "../keyboard-shortcuts";
  import { getScriptTagValue } from "../lib/dom";
  import { log_error } from "../log";
  import { notify } from "../notifications";
  import { lastActiveChartName, showCharts } from "../stores/chart";

  import Chart from "./Chart.svelte";
  import { chartContext } from "./context";
  import ConversionAndInterval from "./ConversionAndInterval.svelte";

  import { chart_data_validator, parseChartData } from ".";
  import type { NamedChartTypes } from ".";

  export let data: unknown;

  let charts: NamedChartTypes[] = [];
  let active_chart: NamedChartTypes | null = null;

  $: if (active_chart) {
    $lastActiveChartName = active_chart.name;
  }

  onMount(() => {
    const chartData = data
      ? chart_data_validator(data)
      : getScriptTagValue("#chart-data", chart_data_validator);

    if (!data && chartData.success && chartData.value.length) {
      notify(
        "This page adds charts using a deprecated method which will be removed soon.",
        "warning"
      );
    }

    const res = parseChartData(chartData, $chartContext);
    if (res.success) {
      charts = res.value;
    } else {
      log_error(res.value);
    }
    active_chart = charts.length
      ? charts.find((c) => c.name === $lastActiveChartName) || charts[0]
      : null;

    if (!active_chart) {
      return () => {
        // noop
      };
    }

    const unbind = [
      bindKey("c", () => {
        const currentIndex = charts.findIndex((e) => e === active_chart);
        active_chart =
          charts[(currentIndex + 1 + charts.length) % charts.length];
      }),
      bindKey("C", () => {
        const currentIndex = charts.findIndex((e) => e === active_chart);
        active_chart =
          charts[(currentIndex - 1 + charts.length) % charts.length];
      }),
    ];

    return () => {
      unbind.forEach((u) => u());
    };
  });
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
          active_chart = chart;
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
