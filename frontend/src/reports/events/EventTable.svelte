<script lang="ts">
  import type { Event } from "../../entries";
  import { _ } from "../../i18n";
  import { DateColumn, Sorter, StringColumn } from "../../sort";
  import SortHeader from "../../sort/SortHeader.svelte";

  export let events: Event[];

  const columns = [
    new DateColumn<Event>(_("Date")),
    new StringColumn<Event>(_("Description"), (d) => d.description),
  ] as const;
  let sorter = new Sorter(columns[0], "desc");

  $: sorted_events = sorter.sort(events);
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
    {#each sorted_events as event}
      <tr>
        <td>{event.date}</td>
        <td>{event.description}</td>
      </tr>
    {/each}
  </tbody>
</table>
