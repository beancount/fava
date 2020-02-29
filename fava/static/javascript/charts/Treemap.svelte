<script>
  import { treemap } from "d3-hierarchy";

  import { favaAPI } from "../stores";
  import { scales } from "./helpers";
  import { formatCurrency, formatPercentage } from "../format";
  import { tooltip } from "./tooltip";

  export let data = [];
  export let width;
  export let currency;
  $: height = Math.min(width / 2.5, 400);

  const tree = treemap().paddingInner(1);
  let root = null;
  let leaves = [];

  $: {
    root = tree.size([width, height])(data);
    leaves = root.leaves();
  }
  function fill(d) {
    const node = d.data.dummy && d.parent ? d.parent : d;
    if (node.depth === 1 || !node.parent) {
      return scales.treemap(node.data.account);
    }
    return scales.treemap(node.parent.data.account);
  }
  function tooltipText(d) {
    const balance = d.value || 0;
    return `${formatCurrency(balance)} ${currency} (${formatPercentage(
      balance / root.value
    )})<em>${d.data.account}</em>`;
  }

  function mouseenter(d) {
    tooltip.style("opacity", 1).html(tooltipText(d));
  }
  function mousemove(event) {
    tooltip
      .style("left", `${event.pageX}px`)
      .style("top", `${event.pageY - 15}px`);
  }
  function mouseleave() {
    tooltip.style("opacity", 0);
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
      on:mouseenter={() => mouseenter(d)}
      on:mousemove={mousemove}
      on:mouseleave={mouseleave}>
      <rect fill={fill(d)} width={d.x1 - d.x0} height={d.y1 - d.y0} />
      <text
        use:setOpacity={d}
        on:click|stopPropagation={() => {
          window.location.href = favaAPI.accountURL.replace('REPLACEME', d.data.account);
        }}
        dy=".5em"
        x={(d.x1 - d.x0) / 2}
        y={(d.y1 - d.y0) / 2}
        text-anchor="middle">
        {d.data.account.split(':').pop() || ''}
      </text>
    </g>
  {/each}
</svg>
