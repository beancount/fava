<script lang="ts">
  import ChartSwitcherTyped from "../../charts/ChartSwitcherTyped.svelte";
  import { day } from "../../format";
  import { _, format } from "../../i18n";
  import { sortableTable } from "../../sort";

  import type { PageData } from "./load";

  export let data: PageData;

  $: charts = data.charts;
  $: groups = data.groups;
</script>

{#if groups.length}
  <ChartSwitcherTyped {charts} />

  {#each groups as [type, events]}
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
          {#each events as event}
            <tr>
              <!-- <td><a href="#context-{event|hash_entry }">{ event.date }</a></td> -->
              <td>{day(event.date)}</td>
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
