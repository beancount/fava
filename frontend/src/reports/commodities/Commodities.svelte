<script lang="ts">
  import type { Commodities } from "../../api/validators";
  import type { FavaChart } from "../../charts";
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import CommodityTable from "./CommodityTable.svelte";

  export let charts: FavaChart[];
  export let commodities: Commodities;
</script>

<ChartSwitcher {charts} />
{#each commodities as { base, quote, prices }}
  <div class="left">
    <h3>{base} / {quote}</h3>
    <CommodityTable {prices} {quote} />
  </div>
{/each}
