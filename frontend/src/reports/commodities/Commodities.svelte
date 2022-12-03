<script lang="ts">
  import ChartSwitcherTyped from "../../charts/ChartSwitcherTyped.svelte";
  import { day } from "../../format";
  import { _ } from "../../i18n";
  import { sortableTable } from "../../sort";
  import { ctx } from "../../stores/format";

  import type { PageData } from "./load";

  export let data: PageData;

  $: charts = data.charts;
  $: commodities = data.commodities;
</script>

<ChartSwitcherTyped {charts} />
{#each commodities as { base, quote, prices }}
  <div class="left">
    <h3>{base} / {quote}</h3>
    <table use:sortableTable>
      <thead>
        <th data-sort="string" data-sort-default="desc" data-order="asc"
          >{_("Date")}</th
        >
        <th data-sort="num">{_("Price")}</th>
      </thead>
      <tbody>
        {#each prices as [date, value]}
          <tr>
            <td>{day(date)}</td>
            <td class="num">{$ctx.amount(value, quote)}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/each}
