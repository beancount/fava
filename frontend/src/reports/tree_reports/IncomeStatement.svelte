<script lang="ts">
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import TreeTable from "../../tree-table/TreeTable.svelte";
  import type { TreeReportProps } from "./index.ts";

  let { charts, trees, date_range }: TreeReportProps = $props();
  let end = $derived(date_range?.end ?? null);
</script>

<ChartSwitcher {charts} />

<div class="row">
  <div class="column">
    {#each trees.slice(0, 2) as tree (tree.account)}
      <TreeTable {tree} {end} />
    {/each}
  </div>
  <div class="column">
    {#each trees.slice(2) as tree (tree.account)}
      <TreeTable {tree} {end} />
    {/each}
  </div>
</div>
