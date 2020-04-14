<script>
  import { treemap } from "d3-hierarchy";

  import router from "../router";
  import { accountUrl } from "../helpers";
  import { treemapScale } from "./helpers";
  import { formatCurrency, formatPercentage } from "../format";
  import { followingTooltip } from "./tooltip";

  export let data;
  export let width;
  export let currency;
  $: height = Math.min(width / 2.5, 400);

  const tree = treemap().paddingInner(1);
  $: root = tree.size([width, height])(data);
  $: leaves = root.leaves().filter((d) => d.value);

  function fill(d) {
    const node = d.data.dummy && d.parent ? d.parent : d;
    if (node.depth === 1 || !node.parent) {
      return $treemapScale(node.data.account);
    }
    return $treemapScale(node.parent.data.account);
  }
  function tooltipText(d) {
    return `${formatCurrency(d.value)} ${currency} (${formatPercentage(
      d.value / root.value
    )})<em>${d.data.account}</em>`;
  }

  function setOpacity(node, param) {
    function update(d) {
      const length = node.getComputedTextLength();
      node.style.opacity = d.x1 - d.x0 > length + 4 && d.y1 - d.y0 > 14 ? 1 : 0;
    }
    update(param);
    return { update };
  }
</script>

<svg class="treemap" {width} {height}>
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
        {d.data.account.split(':').pop() || ''}
      </text>
    </g>
  {/each}
</svg>
