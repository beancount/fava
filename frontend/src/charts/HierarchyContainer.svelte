<script>
  import { getContext } from "svelte";
  import { chartCurrency, chartMode } from "../stores/chart";

  import Sunburst from "./Sunburst.svelte";
  import Treemap from "./Treemap.svelte";

  /** @type {import("svelte/store").Writable<string[]>} */
  const context = getContext("chart-currencies");

  /** @type {Record<string, import(".").AccountHierarchyNode>} */
  export let data;
  /** @type {number} */
  export let width;

  $: currencies = Object.keys(data);
  $: currency = $chartCurrency || currencies[0];
  $: context.set(currencies);
</script>

{#if currencies.length === 0}
  <svg {width}>
    <text x={width / 2} y={80} text-anchor="middle">Chart is empty.</text>
  </svg>
{:else if $chartMode === 'treemap' && data[currency]}
  <Treemap data={data[currency]} {currency} {width} />
{:else if $chartMode === 'sunburst'}
  <svg {width} height={500}>
    {#each currencies as currency, i (currency)}
      <g transform={`translate(${(width * i) / currencies.length},0)`}>
        <Sunburst
          data={data[currency]}
          {currency}
          width={width / currencies.length}
          height={500} />
      </g>
    {/each}
  </svg>
{/if}
