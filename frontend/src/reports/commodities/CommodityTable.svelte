<script lang="ts">
  import { day } from "../../format.ts";
  import { _ } from "../../i18n.ts";
  import { NumberColumn, Sorter } from "../../sort/index.ts";
  import SortHeader from "../../sort/SortHeader.svelte";
  import { ctx } from "../../stores/format.ts";
  import { currency_name } from "../../stores/index.ts";

  type T = [Date, number];
  interface Props {
    prices: readonly T[];
    quote: string;
  }

  let { prices, quote }: Props = $props();

  const columns = [
    new NumberColumn<T>(_("Date"), (d) => d[0].valueOf()),
    new NumberColumn<T>(_("Price"), (d) => d[1]),
  ] as const;
  let sorter = $state(new Sorter(columns[0], "desc"));

  let sorted_prices = $derived(sorter.sort(prices));
  let quote_name = $derived($currency_name(quote));
</script>

<table>
  <thead>
    <tr>
      {#each columns as column (column)}
        <SortHeader bind:sorter {column} />
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each sorted_prices as [date, value] (date)}
      <tr>
        <td>{day(date)}</td>
        <td class="num" title={quote_name}>
          {$ctx.amount(value, quote)}
        </td>
      </tr>
    {/each}
  </tbody>
</table>
