<script lang="ts">
  import { _ } from "../../i18n";
  import { Sorter, StringColumn } from "../../sort";
  import SortHeader from "../../sort/SortHeader.svelte";

  type T = [string, string];
  export let options: Record<string, string>;

  const columns = [
    new StringColumn<T>(_("Key"), (d) => d[0]),
    new StringColumn<T>(_("Value"), (d) => d[1]),
  ] as const;
  let sorter = new Sorter(columns[0], "asc");

  $: options_array = Object.entries(options);
  $: sorted_options = sorter.sort(options_array);
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
    {#each sorted_options as [key, value] (key)}
      <tr>
        <td>{key}</td>
        <td><pre>{value}</pre></td>
      </tr>
    {/each}
  </tbody>
</table>

<style>
  td:nth-child(1) {
    font-weight: 500;
  }
</style>
