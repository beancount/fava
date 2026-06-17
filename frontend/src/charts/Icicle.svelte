<script lang="ts">
  import { partition } from "d3-hierarchy";

  import { urlForAccount } from "../helpers.ts";
  import { leaf } from "../lib/account.ts";
  import { ctx } from "../stores/format.ts";
  import { sunburstScale } from "./helpers.ts";
  import {
    type AccountHierarchyDatum,
    type AccountHierarchyNode,
    balance_with_percentage,
  } from "./hierarchy.ts";
  import { domHelpers, followingTooltip } from "./tooltip.ts";

  interface Props {
    data: AccountHierarchyNode;
    currency: string;
    width: number;
    height: number;
  }

  let { data, currency, width, height }: Props = $props();

  let root = $derived(partition<AccountHierarchyDatum>()(data));
  let nodes = $derived(root.descendants().filter((d) => !d.data.dummy));

  let current = $state<string>();
</script>

<g
  {width}
  {height}
  onmouseleave={() => {
    current = undefined;
  }}
  role="img"
>
  {#each nodes as d (d.data.account)}
    {@const account = d.data.account}
    <g
      {@attach followingTooltip(() => [
        balance_with_percentage($ctx, d, currency),
        domHelpers.em(account),
      ])}
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
