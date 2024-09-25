<!--
  @component
  A query result table.
-->
<script lang="ts">
  import { Amount, Position } from "../../entries";
  import { day } from "../../format";
  import { urlForAccount } from "../../helpers";
  import { is_empty } from "../../lib/objects";
  import AccountIndicator from "../../sidebar/AccountIndicator.svelte";
  import { Sorter, UnsortedColumn } from "../../sort";
  import SortHeader from "../../sort/SortHeader.svelte";
  import { accounts_set } from "../../stores";
  import { ctx, num } from "../../stores/format";
  import type { QueryCell, QueryResultTable } from "./query_table";
  import { Inventory } from "./query_table";

  /** The table to render. */
  export let table: QueryResultTable;
  /** A column name to filter by if empty (expected to be an Inventory column).  */
  export let filter_empty: string | undefined = undefined;

  $: filter_empty_column_number = table.columns.findIndex(
    (column) => column.name === filter_empty,
  );

  $: filtered_rows =
    filter_empty_column_number > -1
      ? table.rows.filter((row) => {
          const cell = row[filter_empty_column_number];
          return !(cell instanceof Inventory && is_empty(cell.value));
        })
      : table.rows;

  let sorter = new Sorter<QueryCell[]>(new UnsortedColumn("<Dummy>"), "asc");
  $: sorted_rows = sorter.sort(filtered_rows);
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
        {#each row as value, index}
          {#if value === null}
            <td>&nbsp;</td>
          {:else if typeof value === "boolean"}
            <td>
              {value.toString().toUpperCase()}
            </td>
          {:else if typeof value === "number"}
            <td class="num">
              {table.columns[index]?.dtype === "int"
                ? value.toString()
                : $num(value)}
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
