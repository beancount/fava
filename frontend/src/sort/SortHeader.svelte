<!--
  @component
  A `<th>` table header for a sortable column.
-->
<script lang="ts">
  import type { SortColumn, Sorter } from ".";

  interface Props {
    /** The current sorter. */
    sorter: Sorter;
    /** The column to show the header for. */
    column: SortColumn;
  }

  let { sorter = $bindable(), column }: Props = $props();
</script>

<th
  onclick={() => {
    sorter = sorter.switchColumn(column);
  }}
  data-order={column === sorter.column ? sorter.order : undefined}
  data-sort
>
  {column.name}
</th>
