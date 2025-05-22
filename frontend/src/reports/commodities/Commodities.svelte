<script lang="ts">
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import type { CommoditiesReportProps } from ".";
  import CommodityTable from "./CommodityTable.svelte";

  let { charts, commodities }: CommoditiesReportProps = $props();
</script>

<ChartSwitcher {charts} />
{#each commodities as { base, quote, prices } (`${base}-${quote}`)}
  <div class="left">
    <h3>{base} / {quote}</h3>
    <CommodityTable {prices} {quote} />
  </div>
{/each}
