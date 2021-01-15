<script>
  import { treemap } from "d3-hierarchy";

  import router from "../router";
  import { accountUrl } from "../helpers";
  import { treemapScale } from "./helpers";
  import { formatCurrency, formatPercentage } from "../format";
  import { followingTooltip } from "./tooltip";

  /** @type {import(".").AccountHierarchyNode} */
  export let data;
  /** @type {number} */
  export let width;
  /** @type {string} */
  export let currency;
  $: height = Math.min(width / 2.5, 400);

  const tree = treemap().paddingInner(1);
  $: root = tree.size([width, height])(data);
  $: leaves = root.leaves().filter((d) => d.value);

  /**
   * @param {import(".").AccountHierarchyNode} d
   */
  function fill(d) {
    const node = d.data.dummy && d.parent ? d.parent : d;
    if (node.depth === 1 || !node.parent) {
      return $treemapScale(node.data.account);
    }
    return $treemapScale(node.parent.data.account);
  }

  /**
   * @param {import(".").AccountHierarchyNode} d
   */
  function tooltipText(d) {
    const val = d.value || 0;
    const rootValue = root.value || 1;

    return `${formatCurrency(val)} ${currency} (${formatPercentage(
      val / rootValue
    )})<em>${d.data.account}</em>`;
  }

  /**
   * @param {SVGTextElement} node
   * @param {import(".").AccountHierarchyNode} param
   */
  function setOpacity(node, param) {
    function update(d) {
      const length = node.getComputedTextLength();
      node.style.opacity =
        d.x1 - d.x0 > length + 4 && d.y1 - d.y0 > 14 ? "1" : "0";
    }
    update(param);
    return { update };
  }
</script>

<svg {width} {height}>
  {#each leaves as d}
    <g
      transform={`translate(${d.x0},${d.y0})`}
      use:followingTooltip={() => tooltipText(d)}>
      <rect fill={fill(d)} width={d.x1 - d.x0} height={d.y1 - d.y0} />
      <text
        use:setOpacity={d}
        on:click={() => router.navigate(accountUrl(d.data.account))}
        dy=".5em"
        x={(d.x1 - d.x0) / 2}
        y={(d.y1 - d.y0) / 2}
        text-anchor="middle">
        {d.data.account.split(":").pop() || ""}
      </text>
    </g>
  {/each}
</svg>

<style>
  svg {
    shape-rendering: crispEdges;
  }

  rect {
    stroke: var(--color-treemap-text);
    stroke-width: 2px;
  }

  text {
    cursor: pointer;
  }
</style>
