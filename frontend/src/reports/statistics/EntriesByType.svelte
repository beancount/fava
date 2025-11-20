<script lang="ts">
  import { sum } from "d3-array";

  import { _ } from "../../i18n.ts";
  import { NumberColumn, Sorter, StringColumn } from "../../sort/index.ts";
  import SortHeader from "../../sort/SortHeader.svelte";

  let { entries_by_type }: { entries_by_type: Record<string, number> } =
    $props();

  let total = $derived(sum(Object.values(entries_by_type)));

  const columns = [
    new StringColumn<[string, number]>(_("Type"), (d) => d[0].valueOf()),
    new NumberColumn<[string, number]>(_("# Entries"), (d) => d[1]),
  ] as const;
  let sorter = $state(new Sorter(columns[0], "asc"));
  let sorted_entries_by_type = $derived(
    sorter.sort(Object.entries(entries_by_type)),
  );
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
    {#each sorted_entries_by_type as [type, count] (type)}
      <tr>
        <td>{type}</td>
        <td class="num">{count}</td>
      </tr>
    {/each}
  </tbody>
  <tfoot>
    <tr>
      <td>{_("Total")}</td>
      <td class="num">{total}</td>
    </tr>
  </tfoot>
</table>
