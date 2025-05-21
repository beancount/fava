<script lang="ts">
  import { partition } from "d3-hierarchy";
  import { scaleLinear } from "d3-scale";
  import { untrack } from "svelte";

  import { formatPercentage } from "../format";
  import { urlForAccount } from "../helpers";
  import { ctx } from "../stores/format";
  import { sunburstScale } from "./helpers";
  import type {
    AccountHierarchyDatum,
    AccountHierarchyNode,
  } from "./hierarchy";
  import { domHelpers, followingTooltip } from "./tooltip";

  interface Props {
    data: AccountHierarchyNode;
    currency: string;
    width: number;
    height: number;
  }

  let { data, currency, width, height }: Props = $props();

  let root = $derived(partition<AccountHierarchyDatum>()(data));
  let nodes = $derived(
    root.descendants().filter((d) => !d.data.dummy && d.depth > 0),
  );

  let current: AccountHierarchyNode | null = $state(null);

  $effect.pre(() => {
    // if-expression to run on each change of chart
    // eslint-disable-next-line @typescript-eslint/no-unused-expressions
    data;
    untrack(() => {
      current = null;
    });
  });

  function balanceText(d: AccountHierarchyNode): string {
    const val = d.value ?? 0;
    const total = root.value ?? 0;
    return total
      ? `${$ctx.amount(val, currency)} (${formatPercentage(val / total)})`
      : $ctx.amount(val, currency);
  }

  let x = $derived(scaleLinear([0, width]));
  let y = $derived(scaleLinear([0, height]));

  function avg(x1: number, x2: number) {
    return (x1 + x2) / 2;
  }

  function tooltipText(d: AccountHierarchyNode) {
    const val = d.value ?? 0;
    const rootValue = root.value ?? 1;

    return [
      domHelpers.t(
        `${$ctx.amount(val, currency)} (${formatPercentage(val / rootValue)})`,
      ),
      domHelpers.em(d.data.account),
    ];
  }
</script>

<g
  {width}
  {height}
  onmouseleave={() => {
    current = null;
  }}
  role="img"
>
  <g
    transform={`translate(${x(avg(root.y0, root.y1)).toString()},${y(avg(root.x0, root.x1)).toString()})`}
  >
    <text class="account" text-anchor="middle">
      {root.data.account}
    </text>
    <text class="balance" dy="1.2em" text-anchor="middle">
      {balanceText(root)}
    </text>
  </g>
  {#each nodes as d}
    <g
      transform={`translate(${x(d.y0).toString()},${y(d.x0).toString()})`}
      use:followingTooltip={() => tooltipText(d)}
    >
      <a href={$urlForAccount(d.data.account)} aria-label={d.data.account}>
        <rect
          fill-rule="evenodd"
          fill={$sunburstScale(d.data.account)}
          class:half={current &&
            !current.data.account.startsWith(d.data.account)}
          onmouseover={() => {
            current = d;
          }}
          onfocus={() => {
            current = d;
          }}
          width={width * (d.y1 - d.y0)}
          height={height * (d.x1 - d.x0)}
          role="img"
        />
        <text
          dy=".5em"
          text-anchor="middle"
          x={x((d.y1 - d.y0) / 2)}
          y={y((d.x1 - d.x0) / 2)}
          visibility={y(d.x1 - d.x0) > 14 ? "visible" : "hidden"}
        >
          {d.data.account.split(":").pop() ?? ""}
        </text>
      </a>
    </g>
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
</style>
