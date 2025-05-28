<script lang="ts">
  import type { HierarchyRectangularNode } from "d3-hierarchy";
  import { treemap } from "d3-hierarchy";
  import type { Action } from "svelte/action";

  import { formatPercentage } from "../format";
  import { urlForAccount } from "../helpers";
  import { leaf } from "../lib/account";
  import { ctx } from "../stores/format";
  import { treemapScale } from "./helpers";
  import type {
    AccountHierarchyDatum,
    AccountHierarchyNode,
  } from "./hierarchy";
  import { domHelpers, followingTooltip } from "./tooltip";

  interface Props {
    data: AccountHierarchyNode;
    width: number;
    height: number;
    currency: string;
  }

  let { data, width, height, currency }: Props = $props();

  const tree = treemap<AccountHierarchyDatum>().paddingInner(2).round(true);
  let root = $derived(tree.size([width, height])(data.copy()));
  let leaves = $derived(
    root.leaves().filter((d) => d.value != null && d.value !== 0),
  );

  function fill(d: AccountHierarchyNode) {
    const node = d.data.dummy && d.parent ? d.parent : d;
    if (node.depth === 1 || !node.parent) {
      return $treemapScale(node.data.account);
    }
    return $treemapScale(node.parent.data.account);
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

  /** Hide account names that are too long. */
  const setVisibility: Action<
    SVGTextElement,
    HierarchyRectangularNode<AccountHierarchyDatum>
  > = (node, param) => {
    function update(d: HierarchyRectangularNode<AccountHierarchyDatum>) {
      const length = node.getComputedTextLength();
      node.style.visibility =
        d.x1 - d.x0 > length + 4 && d.y1 - d.y0 > 14 ? "visible" : "hidden";
    }
    update(param);
    return { update };
  };
</script>

<svg viewBox={`0 0 ${width.toString()} ${height.toString()}`}>
  {#each leaves as d (d.data.account)}
    {@const account = d.data.account}
    <g
      transform={`translate(${d.x0.toString()},${d.y0.toString()})`}
      use:followingTooltip={() => tooltipText(d)}
    >
      <rect fill={fill(d)} width={d.x1 - d.x0} height={d.y1 - d.y0} />
      <a href={$urlForAccount(account)}>
        <text
          use:setVisibility={d}
          dy=".5em"
          x={(d.x1 - d.x0) / 2}
          y={(d.y1 - d.y0) / 2}
          text-anchor="middle"
        >
          {leaf(account)}
        </text>
      </a>
    </g>
  {/each}
</svg>

<style>
  svg {
    shape-rendering: crispedges;
  }
</style>
