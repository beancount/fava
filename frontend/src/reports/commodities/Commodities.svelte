<script lang="ts">
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import { currency_name } from "../../stores/index.ts";
  import CommodityTable from "./CommodityTable.svelte";
  import type { CommoditiesReportProps } from "./index.ts";

  let { charts, commodities }: CommoditiesReportProps = $props();
</script>

<ChartSwitcher {charts} />
{#each commodities as { base, quote, prices } (`${base}-${quote}`)}
  <div class="left">
    <h3>
      <span title={$currency_name(base)}>{base}</span> /
      <span title={$currency_name(quote)}>{quote}</span>
    </h3>
    <CommodityTable {prices} {quote} />
  </div>
{/each}
