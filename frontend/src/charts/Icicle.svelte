<script lang="ts">
  import { partition } from "d3-hierarchy";
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
    root.descendants().filter((d) => !d.data.dummy && d.depth >= 0),
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
  {#each nodes as d (d.data.account)}
    <g
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
          x={width*d.y0}
          y={height*d.x0}
        />
        <text
          dy=".5em"
          text-anchor="middle"
          x={width*(d.y1 + d.y0) / 2}
          y={height*(d.x1 + d.x0) / 2}
          visibility={height*(d.x1 - d.x0) > 14 ? "visible" : "hidden"}
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
</style>
