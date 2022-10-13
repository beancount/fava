<script lang="ts">
  import { get } from "../../api";
  import type { NamedFavaChart } from "../../charts";
  import ChartSwitcherTyped from "../../charts/ChartSwitcherTyped.svelte";
  import { domHelpers } from "../../charts/tooltip";
  import { ctx, day } from "../../format";
  import { _ } from "../../i18n";
  import { should_reload } from "../../router";
  import { sortableTable } from "../../sort";
  import { filter_params } from "../../stores/filters";

  $: load = get("commodities", $filter_params, $should_reload).then(
    (commodities) => {
      const charts: NamedFavaChart[] = commodities.map(
        ({ base, quote, prices }) => {
          const name = `${base} / ${quote}`;
          const values = prices.map((d) => ({ name, date: d[0], value: d[1] }));

          return {
            name,
            type: "linechart",
            data: [{ name, values }],
            tooltipText: (c, d) => [
              domHelpers.t(`1 ${base} = ${c.amount(d.value, quote)}`),
              domHelpers.em(day(d.date)),
            ],
          };
        }
      );
      return { commodities, charts };
    }
  );
</script>

{#await load then { charts, commodities }}
  <ChartSwitcherTyped {charts} />
  {#each commodities as { base, quote, prices }}
    <div class="left">
      <h3>{base} / {quote}</h3>
      <table use:sortableTable>
        <thead>
          <th data-sort="string" data-sort-default="desc" data-order="asc"
            >{_("Date")}</th
          >
          <th data-sort="num">{_("Price")}</th>
        </thead>
        <tbody>
          {#each prices as [date, value]}
            <tr>
              <td>{day(date)}</td>
              <td class="num">{$ctx.amount(value, quote)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/each}
{/await}
