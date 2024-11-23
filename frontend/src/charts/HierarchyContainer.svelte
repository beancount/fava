<script lang="ts">
  import { _ } from "../i18n";
  import { hierarchyChartMode } from "../stores/chart";
  import type { HierarchyChart } from "./hierarchy";
  import Sunburst from "./Sunburst.svelte";
  import Treemap from "./Treemap.svelte";

  interface Props {
    chart: HierarchyChart;
    width: number;
  }

  let { chart, width }: Props = $props();

  let data = $derived(chart.data);
  let currencies = $derived(chart.currencies);

  let treemap_currency = $derived(chart.treemap_currency);
  let mode = $derived($hierarchyChartMode);
  let treemap = $derived(
    mode === "treemap" ? data.get($treemap_currency ?? "") : undefined,
  );
</script>

{#if currencies.length === 0}
  <svg viewBox={`0 0 ${width.toString()} 160`}>
    <text x={width / 2} y={80} text-anchor="middle">
      {_("Chart is empty.")}
    </text>
  </svg>
{:else if treemap && $treemap_currency}
  <Treemap data={treemap} currency={$treemap_currency} {width} />
{:else if mode === "sunburst"}
  <svg viewBox={`0 0 ${width.toString()} 500`}>
    {#each [...data] as [chart_currency, d], i (chart_currency)}
      <g
        transform={`translate(${((width * i) / currencies.length).toString()},0)`}
      >
        <Sunburst
          data={d}
          currency={chart_currency}
          width={width / currencies.length}
          height={500}
        />
      </g>
    {/each}
  </svg>
{/if}
