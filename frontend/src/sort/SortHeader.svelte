<script lang="ts">
  import type { SortColumn, Sorter } from ".";

  export let sorter: Sorter;
  export let column: SortColumn;
</script>

<th
  on:click={() => {
    sorter = sorter.switchColumn(column);
  }}
  data-order={column === sorter.column ? sorter.order : undefined}
  data-sort
>
  {column.name}
</th>
