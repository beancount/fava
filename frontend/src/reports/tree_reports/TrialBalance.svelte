<script lang="ts">
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import TreeTable from "../../tree-table/TreeTable.svelte";
  import type { TreeReportProps } from "./index.ts";

  let { charts, trees, date_range }: TreeReportProps = $props();
  let end = $derived(date_range?.end ?? null);
</script>

<ChartSwitcher {charts} />

<div class="row">
  {#each trees as tree (tree.account)}
    <TreeTable {tree} {end} />
  {/each}
</div>
