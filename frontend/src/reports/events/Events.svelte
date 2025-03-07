<script lang="ts">
  import { group } from "d3-array";

  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import { ScatterPlot } from "../../charts/scatterplot";
  import { _, format } from "../../i18n";
  import type { EventsReportProps } from ".";
  import EventTable from "./EventTable.svelte";

  let { events }: EventsReportProps = $props();

  let groups = $derived([...group(events, (e) => e.type)]);

  let charts = $derived([
    new ScatterPlot(
      _("Events"),
      events.map(({ date, type, description }) => ({
        date: new Date(date),
        type,
        description,
      })),
    ),
  ]);
</script>

{#if groups.length}
  <ChartSwitcher {charts} />

  {#each groups as [type, events_in_group] (type)}
    <div class="left">
      <h3>{format(_("Event: %(type)s"), { type })}</h3>
      <EventTable events={events_in_group} />
    </div>
  {/each}
{:else}
  <p>
    {_("No events.")}
  </p>
{/if}
