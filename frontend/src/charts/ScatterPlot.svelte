<script>
  import { extent } from "d3-array";
  import { axisLeft, axisBottom } from "d3-axis";
  import { scalePoint, scaleUtc } from "d3-scale";
  import { quadtree } from "d3-quadtree";

  import { axis } from "./axis";
  import { scatterplotScale } from "./helpers";
  import { dateFormat } from "../format";
  import { positionedTooltip } from "./tooltip";

  /** @type {import('.').ScatterPlotDatum[]} */
  export let data;
  /** @type {number} */
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

  // Scales
  $: dateExtent = extent(data, (d) => d.date);
  $: x = scaleUtc()
    .domain(dateExtent[0] ? dateExtent : [0, 1])
    .range([0, innerWidth]);
  $: y = scalePoint()
    .padding(1)
    .domain(data.map((d) => d.type))
    .range([innerHeight, 0]);

  // Axes
  $: xAxis = axisBottom(x).tickSizeOuter(0);
  $: yAxis = axisLeft(y)
    .tickPadding(6)
    .tickSize(-innerWidth)
    .tickFormat((d) => d);

  /** Quadtree for hover. */
  $: quad = quadtree(
    data,
    (d) => x(d.date),
    (d) => y(d.type) || 0
  );

  /**
   * @param {import('.').ScatterPlotDatum} d
   * @returns {string}
   */
  function tooltipText(d) {
    return `${d.description}<em>${dateFormat.day(d.date)}</em>`;
  }

  /**
   * @param {number} xPos
   * @param {number} yPos
   * @returns {[number, number, string] | undefined}
   */
  function tooltipInfo(xPos, yPos) {
    const d = quad.find(xPos, yPos);
    return d ? [x(d.date), y(d.type) || 0, tooltipText(d)] : undefined;
  }
</script>

<svg {width} {height}>
  <g
    use:positionedTooltip={tooltipInfo}
    transform={`translate(${margin.left},${margin.top})`}>
    <g
      class="x axis"
      use:axis={xAxis}
      transform={`translate(0,${innerHeight})`}
    />
    <g class="y axis" use:axis={yAxis} />
    <g>
      {#each data as dot}
        <circle
          r="5"
          fill={scatterplotScale(dot.type)}
          cx={x(dot.date)}
          cy={y(dot.type)}
        />
      {/each}
    </g>
  </g>
</svg>

<style>
  svg > g {
    pointer-events: all;
  }
</style>
