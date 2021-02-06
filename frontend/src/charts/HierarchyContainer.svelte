<script>
  import { getContext } from "svelte";
  import { chartCurrency, hierarchyChartMode } from "../stores/chart";

  import Sunburst from "./Sunburst.svelte";
  import Treemap from "./Treemap.svelte";

  /** @type {import("svelte/store").Writable<string[]>} */
  const context = getContext("chart-currencies");

  /** @type {import(".").HierarchyChart['data']} */
  export let data;
  /** @type {number} */
  export let width;

  $: currencies = [...data.keys()];
  $: currency = $chartCurrency || currencies[0];
  $: context.set(currencies);
</script>

{#if currencies.length === 0}
  <svg {width}>
    <text x={width / 2} y={80} text-anchor="middle">Chart is empty.</text>
  </svg>
{:else if $hierarchyChartMode === "treemap" && data.get(currency)}
  <Treemap data={data.get(currency)} {currency} {width} />
{:else if $hierarchyChartMode === "sunburst"}
  <svg {width} height={500}>
    {#each [...data] as [currency, d], i (currency)}
      <g transform={`translate(${(width * i) / currencies.length},0)`}>
        <Sunburst
          data={d}
          {currency}
          width={width / currencies.length}
          height={500}
        />
      </g>
    {/each}
  </svg>
{/if}
