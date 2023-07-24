<script lang="ts">
  import ChartSwitcher from "../../charts/ChartSwitcher.svelte";
  import { day } from "../../format";
  import { _, format } from "../../i18n";
  import { sortableTable } from "../../sort";

  import type { PageData } from "./load";

  export let charts: PageData["charts"];
  export let groups: PageData["groups"];
</script>

{#if groups.length}
  <ChartSwitcher {charts} />

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
