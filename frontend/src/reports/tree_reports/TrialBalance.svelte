<script lang="ts">
  import { parseChartData } from "../../charts";
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import { chartContext } from "../../charts/context";
  import TreeTable from "../../tree-table/TreeTable.svelte";
  import type { TreeReportProps } from ".";

  let { charts, trees, date_range }: TreeReportProps = $props();
  let end = $derived(date_range?.end ?? null);

  let chartData = $derived(
    parseChartData(charts, $chartContext).unwrap_or(null),
  );
</script>

{#if chartData}
  <ChartSwitcher charts={chartData} />
{/if}

<div class="row">
  {#each trees as tree}
    <TreeTable {tree} {end} />
  {/each}
</div>
