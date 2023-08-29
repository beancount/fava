<script lang="ts">
  import { group } from "d3-array";

  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import { ScatterPlot } from "../../charts/scatterplot";
  import type { Event } from "../../entries";
  import { _, format } from "../../i18n";
  import { sortableTable } from "../../sort";

  export let events: Event[];

  $: groups = [...group(events, (e) => e.type)];

  $: charts = [
    new ScatterPlot(
      _("Events"),
      events.map(({ date, type, description }) => ({
        date: new Date(date),
        type,
        description,
      }))
    ),
  ];
</script>

{#if groups.length}
  <ChartSwitcher {charts} />

  {#each groups as [type, events_in_group]}
    <div class="left">
      <h3>{format(_("Event: %(type)s"), { type })}</h3>
      <table use:sortableTable>
        <thead>
          <tr>
            <th data-sort="string" data-order="asc">{_("Date")}</th>
            <th data-sort="string">{_("Description")}</th>
          </tr>
        </thead>
        <tbody>
          {#each events_in_group as event}
            <tr>
              <!-- <td><a href="#context-{event|hash_entry }">{ event.date }</a></td> -->
              <td>{event.date}</td>
              <td>{event.description}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/each}
{:else}
  <p>
    {_("No events.")}
  </p>
{/if}
