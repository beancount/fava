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

  interface Props {
    /** The table to render. */
    table: QueryResultTable;
    /** A column name to filter by if empty (expected to be an Inventory column).  */
    filter_empty?: string;
  }

  let { table, filter_empty }: Props = $props();

  let filter_empty_column_index = $derived(
    table.columns.findIndex((column) => column.name === filter_empty),
  );

  let filtered_rows = $derived(
    filter_empty_column_index > -1
      ? table.rows.filter((row) => {
          const cell = row[filter_empty_column_index];
          return !(cell instanceof Inventory && is_empty(cell.value));
        })
      : table.rows,
  );

  let sorter = $state.raw(
    new Sorter<QueryCell[]>(new UnsortedColumn("<Dummy>"), "asc"),
  );
  let sorted_rows = $derived(sorter.sort(filtered_rows));
</script>

<table>
  <thead>
    <tr>
      {#each table.columns as column (column.name)}
        <SortHeader bind:sorter {column} />
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each sorted_rows as row (row)}
      <tr>
        {#each row as value, index (index)}
          {#if value == null}
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
              {#each Object.entries(value.value) as [currency, number] (currency)}
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
