<script lang="ts">
  import type { HierarchyRectangularNode } from "d3-hierarchy";
  import { partition } from "d3-hierarchy";
  import { scaleLinear, scaleSqrt } from "d3-scale";
  import { arc } from "d3-shape";

  import { formatPercentage } from "../format";
  import { urlForAccount } from "../helpers";
  import { ctx } from "../stores/format";
  import { sunburstScale } from "./helpers";
  import type {
    AccountHierarchyDatum,
    AccountHierarchyNode,
  } from "./hierarchy";

  export let data: AccountHierarchyNode;
  export let currency: string;
  export let width: number;
  export let height: number;

  $: radius = Math.min(width, height) / 2;

  $: root = partition<AccountHierarchyDatum>()(data);
  $: nodes = root.descendants().filter((d) => !d.data.dummy && d.depth);

  let current: AccountHierarchyNode | null = null;

  // if-expression to run labelled statement on each change of root
  // eslint-disable-next-line @typescript-eslint/strict-boolean-expressions
  $: if (root) {
    current = null;
  }

  function balanceText(d: AccountHierarchyNode): string {
    const val = d.value ?? 0;
    const total = root.value ?? 0;
    return total
      ? `${$ctx.amount(val, currency)} (${formatPercentage(val / total)})`
      : $ctx.amount(val, currency);
  }

  const x = scaleLinear([0, 2 * Math.PI]);
  $: y = scaleSqrt([0, radius]);
  $: arcShape = arc<HierarchyRectangularNode<AccountHierarchyDatum>>()
    .startAngle((d) => x(d.x0))
    .endAngle((d) => x(d.x1))
    .innerRadius((d) => y(d.y0))
    .outerRadius((d) => y(d.y1));
</script>

<g
  {width}
  {height}
  transform={`translate(${(width / 2).toString()},${(height / 2).toString()})`}
  on:mouseleave={() => {
    current = null;
  }}
  role="img"
>
  <circle style="opacity:0" r={radius} />
  <text class="account" text-anchor="middle">
    {(current ?? root).data.account}
  </text>
  <text class="balance" dy="1.2em" text-anchor="middle">
    {balanceText(current ?? root)}
  </text>
  {#each nodes as d}
    <a href={$urlForAccount(d.data.account)}>
      <path
        on:mouseover={() => {
          current = d;
        }}
        on:focus={() => {
          current = d;
        }}
        class:half={current && !current.data.account.startsWith(d.data.account)}
        fill-rule="evenodd"
        fill={$sunburstScale(d.data.account)}
        d={arcShape(d)}
        role="img"
      />
    </a>
  {/each}
</g>

<style>
  .half {
    opacity: 0.5;
  }

  .account {
    fill: var(--text-color);
  }

  .balance {
    font-family: var(--font-family-monospaced);
  }

  path {
    cursor: pointer;
  }
</style>
