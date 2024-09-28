<script lang="ts">
  import type { Writable } from "svelte/store";

  import { _ } from "../i18n";
  import { hierarchyChartMode, treemapCurrency } from "../stores/chart";
  import type { HierarchyChart } from "./hierarchy";
  import Sunburst from "./Sunburst.svelte";
  import Treemap from "./Treemap.svelte";

  export let chart: HierarchyChart;
  export let width: number;
  export let treemap_currencies: Writable<string[]>;

  $: data = chart.data;
  $: currencies = [...data.keys()];
  $: treemap_currencies.set(currencies);

  $: if ($treemapCurrency === null) {
    $treemapCurrency = $treemapCurrency ?? currencies[0] ?? null;
  }

  $: currency = $treemapCurrency;

  $: mode = $hierarchyChartMode;
  $: treemap = mode === "treemap" ? data.get(currency ?? "") : undefined;
</script>

{#if currencies.length === 0}
  <svg viewBox={`0 0 ${width.toString()} 160`}>
    <text x={width / 2} y={80} text-anchor="middle">
      {_("Chart is empty.")}
    </text>
  </svg>
{:else if treemap && currency}
  <Treemap data={treemap} {currency} {width} />
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
