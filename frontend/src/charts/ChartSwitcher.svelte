<script lang="ts">
  import { onMount } from "svelte";

  import { log_error } from "../log";

  import ChartSwitcherTyped from "./ChartSwitcherTyped.svelte";
  import { chartContext } from "./context";

  import { chart_data_validator, parseChartData } from ".";
  import type { NamedFavaChart } from ".";

  export let data: unknown;

  let charts: NamedFavaChart[] = [];

  onMount(() => {
    const chartData = chart_data_validator(data);

    const res = parseChartData(chartData, $chartContext);
    if (res.success) {
      charts = res.value;
    } else {
      log_error(res.value);
    }
  });
</script>

{#if charts.length > 0}
  <ChartSwitcherTyped {charts} />
{/if}
