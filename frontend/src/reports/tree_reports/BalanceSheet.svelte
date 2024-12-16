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
  <div class="column">
    {#each trees.slice(0, 1) as tree}
      <TreeTable {tree} {end} />
    {/each}
  </div>
  <div class="column">
    {#each trees.slice(1) as tree}
      <TreeTable {tree} {end} />
    {/each}
  </div>
</div>
