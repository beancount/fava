<script lang="ts">
  import { extent } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { quadtree } from "d3-quadtree";
  import { scalePoint, scaleUtc } from "d3-scale";

  import { day } from "../format.ts";
  import Axis from "./Axis.svelte";
  import Brush from "./Brush.svelte";
  import { scatterplotScale } from "./helpers.ts";
  import type { ScatterPlot, ScatterPlotDatum } from "./scatterplot.ts";
  import type { TooltipFindNode } from "./tooltip.ts";
  import { domHelpers } from "./tooltip.ts";

  interface Props {
    chart: ScatterPlot;
    width: number;
  }

  let { chart, width }: Props = $props();

  const today = new Date();

  // Constant dimensions
  const margin = { top: 10, right: 10, bottom: 30, left: 70 };
  const height = 250;
  const inner_height = height - margin.top - margin.bottom;

  // Derived dimensions
  let inner_width = $derived(width - margin.left - margin.right);

  // Scales
  let date_extent = $derived(extent(chart.data, (d) => d.date));
  let x = $derived(
    scaleUtc([0, inner_width]).domain(date_extent[0] ? date_extent : [0, 1]),
  );
  let y = $derived(
    scalePoint([inner_height, 0])
      .domain(chart.data.map((d) => d.type))
      .padding(1),
  );

  // Axes
  let x_axis = $derived(axisBottom(x).tickSizeOuter(0));
  let y_axis = $derived(
    axisLeft(y)
      .tickPadding(6)
      .tickSize(-inner_width)
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
    return [d.description, domHelpers.em(day(d.date))];
  }

  const tooltip_find: TooltipFindNode = (x_pointer, y_pointer) => {
    const d = quad.find(x_pointer, y_pointer);
    return d && [x(d.date), y(d.type) ?? 0, tooltipText(d)];
  };
</script>

<svg viewBox={`0 0 ${width.toString()} ${height.toString()}`}>
  <Brush
    invert={x.invert.bind(x)}
    height={inner_height}
    find={tooltip_find}
    transform={`translate(${margin.left.toString()},${margin.top.toString()})`}
  >
    <Axis x axis={x_axis} {inner_height} />
    <Axis y axis={y_axis} />
    <g>
      {#each chart.data as dot (`${dot.date.toString()}-${dot.type}`)}
        <circle
          r="5"
          fill={scatterplotScale(dot.type)}
          cx={x(dot.date)}
          cy={y(dot.type)}
          class:desaturate={dot.date > today}
        />
      {/each}
    </g>
  </Brush>
</svg>

<style>
  .desaturate {
    filter: saturate(50%);
  }
</style>
