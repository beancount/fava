<script lang="ts">
  import { extent } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { quadtree } from "d3-quadtree";
  import { scalePoint, scaleUtc } from "d3-scale";

  import { day } from "../format";
  import Axis from "./Axis.svelte";
  import { scatterplotScale } from "./helpers";
  import type { ScatterPlot, ScatterPlotDatum } from "./scatterplot";
  import type { TooltipFindNode } from "./tooltip";
  import { domHelpers, positionedTooltip } from "./tooltip";

  interface Props {
    chart: ScatterPlot;
    width: number;
  }

  let { chart, width }: Props = $props();

  const today = new Date();
  const margin = { top: 10, right: 10, bottom: 30, left: 70 };
  const height = 250;
  let innerWidth = $derived(width - margin.left - margin.right);
  let innerHeight = $derived(height - margin.top - margin.bottom);

  // Scales
  let dateExtent = $derived(extent(chart.data, (d) => d.date));
  let x = $derived(
    scaleUtc([0, innerWidth]).domain(dateExtent[0] ? dateExtent : [0, 1]),
  );
  let y = $derived(
    scalePoint([innerHeight, 0])
      .domain(chart.data.map((d) => d.type))
      .padding(1),
  );

  // Axes
  let xAxis = $derived(axisBottom(x).tickSizeOuter(0));
  let yAxis = $derived(
    axisLeft(y)
      .tickPadding(6)
      .tickSize(-innerWidth)
      .tickFormat((d) => d),
  );

  /** Quadtree for hover. */
  let quad = $derived(
    quadtree(
      [...chart.data],
      (d) => x(d.date),
      (d) => y(d.type) ?? 0,
    ),
  );

  function tooltipText(d: ScatterPlotDatum) {
    return [domHelpers.t(d.description), domHelpers.em(day(d.date))];
  }

  const tooltipFindNode: TooltipFindNode = (xPos, yPos) => {
    const d = quad.find(xPos, yPos);
    return d && [x(d.date), y(d.type) ?? 0, tooltipText(d)];
  };
</script>

<svg viewBox={`0 0 ${width.toString()} ${height.toString()}`}>
  <g
    use:positionedTooltip={tooltipFindNode}
    transform={`translate(${margin.left.toString()},${margin.top.toString()})`}
  >
    <Axis x axis={xAxis} {innerHeight} />
    <Axis y axis={yAxis} />
    <g>
      {#each chart.data as dot}
        <circle
          r="5"
          fill={scatterplotScale(dot.type)}
          cx={x(dot.date)}
          cy={y(dot.type)}
          class:desaturate={dot.date > today}
        />
      {/each}
    </g>
  </g>
</svg>

<style>
  svg > g {
    pointer-events: all;
  }

  .desaturate {
    filter: saturate(50%);
  }
</style>
