<script lang="ts">
  import { extent, group } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { pathRound } from "d3-path";
  import { quadtree } from "d3-quadtree";
  import { scalePoint, scaleUtc } from "d3-scale";

  import { day } from "../format.ts";
  import Axis from "./Axis.svelte";
  import Brush from "./Brush.svelte";
  import { scatterplot_scale } from "./helpers.ts";
  import type { ScatterPlot, ScatterPlotDatum } from "./scatterplot.ts";
  import type { TooltipFindNode } from "./tooltip.ts";
  import { domHelpers } from "./tooltip.ts";

  interface Props {
    chart: ScatterPlot;
    width: number;
  }

  let { chart, width }: Props = $props();

  const uid = $props.id();
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

  let dots_by_type = $derived(group(chart.data, (d) => d.type));

  const dots_shape = (dots: readonly ScatterPlotDatum[]) => {
    const path = pathRound(1);
    for (const d of dots) {
      const cx = x(d.date);
      const cy = y(d.type) ?? 0;
      path.moveTo(cx + 5, cy);
      path.arc(cx, cy, 5, 0, 2 * Math.PI);
    }
    return path.toString();
  };

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

  function tooltip_text(d: ScatterPlotDatum) {
    return [d.description, domHelpers.em(day(d.date))];
  }

  const tooltip_find: TooltipFindNode = (x_pointer, y_pointer) => {
    const d = quad.find(x_pointer, y_pointer);
    return d && [x(d.date), y(d.type) ?? 0, d, () => tooltip_text(d)];
  };

  let desaturate_filter_id = $derived(`desaturate-future-${uid}`);
  let desaturate_future_filter = $derived(
    (date_extent[1] ?? today) > today
      ? `url(#${desaturate_filter_id})`
      : undefined,
  );
</script>

<svg viewBox={`0 0 ${width.toString()} ${height.toString()}`}>
  <defs>
    <filter id={desaturate_filter_id}>
      <feColorMatrix type="saturate" values="0.5" x={x(today)} />
      <feBlend in2="SourceGraphic" />
    </filter>
  </defs>
  <Brush
    invert={x.invert.bind(x)}
    height={inner_height}
    find={tooltip_find}
    transform={`translate(${margin.left.toString()},${margin.top.toString()})`}
  >
    <Axis x axis={x_axis} {inner_height} />
    <Axis y axis={y_axis} />
    <g filter={desaturate_future_filter}>
      {#each dots_by_type as [type, dots] (type)}
        <path d={dots_shape(dots)} fill={scatterplot_scale(type)} />
      {/each}
    </g>
  </Brush>
</svg>
