<script lang="ts">
  import { parseChartData } from "../../charts";
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import { chartContext } from "../../charts/context";
  import type { AccountTreeNode } from "../../charts/hierarchy";
  import TreeTable from "../../tree-table/TreeTable.svelte";

  export let charts: unknown;
  export let trees: AccountTreeNode[];
  export let date_range: { begin: Date; end: Date } | null;

  $: chartData = parseChartData(charts, $chartContext).unwrap_or(null);
</script>

{#if chartData}
  <ChartSwitcher charts={chartData} />
{/if}

<div class="row">
  {#each trees as tree}
    <TreeTable {tree} end={date_range?.end ?? null} />
  {/each}
</div>
