<script>
  import { extent } from "d3-array";
  import { axisLeft, axisBottom } from "d3-axis";
  import { scalePoint, scaleUtc } from "d3-scale";
  import { select } from "d3-selection";
  import { quadtree } from "d3-quadtree";

  import { scales } from "./helpers";
  import { dateFormat } from "../format";
  import { positionedTooltip } from "./tooltip";

  export let data;
  export let width;
  const margin = {
    top: 10,
    right: 10,
    bottom: 30,
    left: 70,
  };
  const height = 250;
  $: innerWidth = width - margin.left - margin.right;
  $: innerHeight = height - margin.top - margin.bottom;

  // Elements
  let xAxisElement;
  let yAxisElement;

  // Scales
  let x = scaleUtc();
  let y = scalePoint().padding(1);
  $: {
    x = x.range([0, innerWidth]);
    y = y.range([innerHeight, 0]);
  }
  $: {
    const dateExtent = extent(data, d => d.date);
    if (dateExtent[0] !== undefined) {
      x = x.domain(dateExtent);
    }
    y = y.domain(data.map(d => d.type));
  }

  // Axes
  const xAxis = axisBottom(x).tickSizeOuter(0);
  let yAxis = axisLeft(y)
    .tickPadding(6)
    .tickFormat(d => d);
  $: yAxis = yAxis.tickSize(-innerWidth);
  $: if (x && y && yAxisElement && xAxisElement) {
    xAxis(select(xAxisElement));
    yAxis(select(yAxisElement));
  }

  // Quadtree for hover.
  $: quad = quadtree(
    data,
    d => x(d.date),
    d => y(d.type)
  );
  function tooltipText(d) {
    return `${d.description}<em>${dateFormat.day(d.date)}</em>`;
  }

  function tooltipInfo(...pos) {
    const d = quad.find(...pos);
    return d ? [x(d.date), y(d.type), tooltipText(d)] : undefined;
  }
</script>

<svg class="scatterplot" {width} {height}>
  <g
    use:positionedTooltip={tooltipInfo}
    transform={`translate(${margin.left},${margin.top})`}>
    <g
      class="x axis"
      bind:this={xAxisElement}
      transform={`translate(0,${innerHeight})`} />
    <g class="y axis" bind:this={yAxisElement} />
    <g>
      {#each data as dot}
        <circle
          r="5"
          fill={scales.scatterplot(dot.type)}
          cx={x(dot.date)}
          cy={y(dot.type)} />
      {/each}
    </g>
  </g>
</svg>
