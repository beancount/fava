<script lang="ts">
  import { partition } from "d3-hierarchy";

  import { formatPercentage } from "../format";
  import { urlForAccount } from "../helpers";
  import { leaf } from "../lib/account";
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
  let nodes = $derived(root.descendants().filter((d) => !d.data.dummy));

  let current: string | null = $state(null);

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
    {@const account = d.data.account}
    <g
      use:followingTooltip={() => tooltipText(d)}
      class:current={current != null ? current.startsWith(account) : false}
    >
      <a
        href={$urlForAccount(account)}
        aria-label={account}
        onmouseover={() => {
          current = account;
        }}
        onfocus={() => {
          current = account;
        }}
      >
        <rect
          fill-rule="evenodd"
          fill={$sunburstScale(account)}
          width={width * (d.y1 - d.y0)}
          height={height * (d.x1 - d.x0)}
          role="img"
          x={width * d.y0}
          y={height * d.x0}
        />
        <text
          dy=".5em"
          text-anchor="middle"
          x={(width * (d.y1 + d.y0)) / 2}
          y={(height * (d.x1 + d.x0)) / 2}
          visibility={height * (d.x1 - d.x0) > 14 ? "visible" : "hidden"}
        >
          {leaf(account)}
        </text>
      </a>
    </g>
  {/each}
</g>

<style>
  g:focus-within > g,
  g:hover > g {
    opacity: 0.7;
  }

  g:focus-within > g.current,
  g:hover > g.current {
    opacity: 1;
  }
</style>
