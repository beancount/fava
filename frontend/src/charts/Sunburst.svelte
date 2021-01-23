<script>
  import { partition } from "d3-hierarchy";
  import { scaleLinear, scaleSqrt } from "d3-scale";
  import { arc } from "d3-shape";

  import router from "../router";
  import { accountUrl } from "../helpers";
  import { sunburstScale } from "./helpers";
  import { formatCurrency, formatPercentage } from "../format";

  /** @type {import(".").AccountHierarchyNode} */
  export let data;
  /** @type {string} */
  export let currency;
  /** @type {number} */
  export let width;
  /** @type {number} */
  export let height;

  $: radius = Math.min(width, height) / 2;

  /**
   * @param {import(".").AccountHierarchyNode} d
   * @returns {string}
   */
  function balanceText(d) {
    const val = d.value || 0;
    const rootVal = root.value || 1;
    return `${formatCurrency(val)} ${currency} (${formatPercentage(
      val / rootVal
    )})`;
  }

  $: root = partition()(data);
  $: leaves = root.descendants().filter((d) => !d.data.dummy && d.depth);

  /** @type {import(".").AccountHierarchyNode | null} */
  let current = null;
  $: if (root) {
    current = null;
  }
  $: currentAccount = current ? current.data.account : root.data.account;
  $: currentBalance = current ? balanceText(current) : balanceText(root);

  const x = scaleLinear().range([0, 2 * Math.PI]);
  $: y = scaleSqrt().range([0, radius]);
  $: arcShape = arc()
    .startAngle((d) => x(d.x0))
    .endAngle((d) => x(d.x1))
    .innerRadius((d) => y(d.y0))
    .outerRadius((d) => y(d.y1));
</script>

<g
  {width}
  {height}
  transform={`translate(${width / 2},${height / 2})`}
  on:mouseleave={() => {
    current = null;
  }}
>
  <circle style="opacity:0" r={radius} />
  <text class="account" text-anchor="middle">
    {currentAccount || root.data.account}
  </text>
  <text class="balance" dy="1.2em" text-anchor="middle">{currentBalance}</text>
  {#each leaves as d}
    <path
      on:click={() => router.navigate(accountUrl(d.data.account))}
      on:mouseover={() => {
        current = d;
      }}
      class:half={current && !currentAccount.startsWith(d.data.account)}
      fill-rule="evenodd"
      fill={$sunburstScale(d.data.account)}
      d={arcShape(d)}
    />
  {/each}
</g>

<style>
  .half {
    opacity: 0.5;
  }
  .account {
    fill: var(--color-text);
  }
  .balance {
    font-family: var(--font-family-monospaced);
  }
  path {
    cursor: pointer;
  }
</style>
