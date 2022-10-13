<script lang="ts">
  import { group } from "d3-array";

  import { get } from "../../api";
  import type { NamedFavaChart } from "../../charts";
  import ChartSwitcherTyped from "../../charts/ChartSwitcherTyped.svelte";
  import { day } from "../../format";
  import { _, format } from "../../i18n";
  import { should_reload } from "../../router";
  import { sortableTable } from "../../sort";
  import { filter_params } from "../../stores/filters";

  $: load = get("events", $filter_params, $should_reload).then((events) => {
    const groups = [...group(events, (e) => e.type)];

    const charts: NamedFavaChart[] = [
      { name: _("Events"), type: "scatterplot", data: events },
      ...groups.map(
        ([type, data]): NamedFavaChart => ({
          name: format(_("Event: %(type)s"), { type }),
          type: "scatterplot",
          data,
        })
      ),
    ];

    return { charts, groups };
  });
</script>

{#await load then { charts, groups }}
  <!-- eslint-disable-next-line no-undef -->
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
{/await}
