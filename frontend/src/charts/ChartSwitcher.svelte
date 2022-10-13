<script lang="ts">
  import { onMount } from "svelte";

  import { getScriptTagValue } from "../lib/dom";
  import { log_error } from "../log";
  import { notify } from "../notifications";

  import ChartSwitcherTyped from "./ChartSwitcherTyped.svelte";
  import { chartContext } from "./context";

  import { chart_data_validator, parseChartData } from ".";
  import type { NamedFavaChart } from ".";

  export let data: unknown;

  let charts: NamedFavaChart[] = [];

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
  });
</script>

{#if charts.length > 0}
  <ChartSwitcherTyped {charts} />
{/if}
