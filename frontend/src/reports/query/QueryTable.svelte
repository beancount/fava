<!--
  @component
  A query result table.
-->
<script lang="ts">
  import { Amount, Position } from "../../entries";
  import { day } from "../../format";
  import { urlForAccount } from "../../helpers";
  import AccountIndicator from "../../sidebar/AccountIndicator.svelte";
  import { Sorter, UnsortedColumn } from "../../sort";
  import SortHeader from "../../sort/SortHeader.svelte";
  import { accounts_set } from "../../stores";
  import { ctx, num } from "../../stores/format";

  import { Inventory } from "./query_table";
  import type { QueryCell, QueryResultTable } from "./query_table";

  /** The table to render. */
  export let table: QueryResultTable;

  // TODO: filter empty for e.g. the holdings report
  // done previously in the HTML with
  // {% for row in rows if filter_empty == None or not row[filter_empty].is_empty() %}

  let sorter = new Sorter<QueryCell[]>(new UnsortedColumn("<Dummy>"), "asc");
  $: sorted_rows = sorter.sort(table.rows);
</script>

<table>
  <thead>
    <tr>
      {#each table.columns as column}
        <SortHeader bind:sorter {column} />
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each sorted_rows as row}
      <tr>
        {#each row as value}
          {#if value === null}
            <td>&nbsp;</td>
          {:else if typeof value === "boolean"}
            <td>
              {value.toString().toUpperCase()}
            </td>
          {:else if typeof value === "number"}
            <td class="num">
              {$num(value)}
            </td>
          {:else if typeof value === "string"}
            <td>
              {#if $accounts_set.has(value)}
                <a href={$urlForAccount(value)}>{value}</a>
                <AccountIndicator account={value} small />
              {:else if value.length === 32 && /[a-z0-9]/.test(value)}
                <a href={`#context-${value}`}>{value}</a>
              {:else}
                {value}
              {/if}
            </td>
          {:else if Array.isArray(value)}
            <td>
              {value.join(",")}
            </td>
          {:else if value instanceof Date}
            <td>
              {day(value)}
            </td>
          {:else if value instanceof Amount}
            <td class="num">
              {value.str($ctx)}
            </td>
          {:else if value instanceof Position}
            <td class="num">
              {value.units.str($ctx)}
              {#if value.cost}
                &lbrace;{value.cost.str($ctx)}&rbrace;{/if}
            </td>
          {:else if value instanceof Inventory}
            <td class="num">
              {#each Object.entries(value.value) as [currency, number]}
                {$ctx.amount(number, currency)}
                <br />
              {/each}
            </td>
          {/if}
        {/each}
      </tr>
    {/each}
  </tbody>
</table>
