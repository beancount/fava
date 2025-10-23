<!--
  @component
  A `<th>` table header for a sortable column.
-->
<script lang="ts">
  import { type SortColumn, type Sorter, UnsortedColumn } from "./index.ts";

  interface Props {
    /** The current sorter. */
    sorter: Sorter;
    /** The column to show the header for. */
    column: SortColumn;
  }

  let { sorter = $bindable(), column }: Props = $props();

  let is_sortable = $derived(!(column instanceof UnsortedColumn));
</script>

{#if is_sortable}
  <th
    onclick={() => {
      sorter = sorter.switchColumn(column);
    }}
    data-order={column === sorter.column ? sorter.order : undefined}
    data-sort
  >
    {column.name}
  </th>
{:else}
  <th>
    {column.name}
  </th>
{/if}
