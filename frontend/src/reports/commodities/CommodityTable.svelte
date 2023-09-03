<script lang="ts">
  import { day } from "../../format";
  import { _ } from "../../i18n";
  import { NumberColumn, Sorter } from "../../sort";
  import SortHeader from "../../sort/SortHeader.svelte";
  import { ctx } from "../../stores/format";

  type T = [Date, number];
  export let prices: readonly T[];
  export let quote: string;

  const columns = [
    new NumberColumn<T>(_("Date"), (d) => d[0].valueOf()),
    new NumberColumn<T>(_("Price"), (d) => d[1]),
  ] as const;
  let sorter = new Sorter(columns[0], "desc");

  $: sorted_prices = sorter.sort(prices);
</script>

<table>
  <thead>
    <tr>
      {#each columns as column}
        <SortHeader bind:sorter {column} />
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each sorted_prices as [date, value] (date)}
      <tr>
        <td>{day(date)}</td>
        <td class="num">{$ctx.amount(value, quote)}</td>
      </tr>
    {/each}
  </tbody>
</table>
