<script lang="ts">
  import type { Event } from "../../entries";
  import { _ } from "../../i18n";
  import { DateColumn, Sorter, StringColumn } from "../../sort";
  import SortHeader from "../../sort/SortHeader.svelte";

  interface Props {
    events: Event[];
  }

  let { events }: Props = $props();

  const columns = [
    new DateColumn<Event>(_("Date")),
    new StringColumn<Event>(_("Description"), (d) => d.description),
  ] as const;
  let sorter = $state(new Sorter(columns[0], "desc"));

  let sorted_events = $derived(sorter.sort(events));
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
    {#each sorted_events as event (`${event.date}-${event.description}`)}
      <tr>
        <td>{event.date}</td>
        <td>{event.description}</td>
      </tr>
    {/each}
  </tbody>
</table>
