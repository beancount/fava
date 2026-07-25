<script lang="ts">
  import { extent, max, min } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { quadtree } from "d3-quadtree";
  import { scaleLinear, scaleUtc } from "d3-scale";
  import { area, curveStepAfter, line } from "d3-shape";

  import { chartToggledCurrencies, lineChartMode } from "../stores/chart.ts";
  import { ctx, short } from "../stores/format.ts";
  import Axis from "./Axis.svelte";
  import Brush from "./Brush.svelte";
  import { currenciesScale, includeZero, padExtent } from "./helpers.ts";
  import type { LineChart, LineChartDatum } from "./line.ts";
  import type { TooltipFindNode } from "./tooltip.ts";

  interface Props {
    chart: LineChart;
    width: number;
  }

  let { chart, width }: Props = $props();

  const uid = $props.id();
  const today = new Date();

  // Constant dimensions
  const margin = { top: 10, right: 10, bottom: 30, left: 40 };
  const height = 250;
  const inner_height = height - margin.top - margin.bottom;

  // Derived dimensions
  let inner_width = $derived(width - margin.left - margin.right);

  let data = $derived(chart.filter($chartToggledCurrencies));

  // Scales and quadtree
  let all_values = $derived(data.flatMap((d) => d.values));

  let x_extent = $derived([
    min(data, (s) => s.values[0]?.date) ?? today,
    max(data, (s) => s.values[s.values.length - 1]?.date) ?? today,
  ] as const);
  let x = $derived(scaleUtc([0, inner_width]).domain(x_extent));
  let value_extent = $derived(extent(all_values, (v) => v.value));
  // Include zero in area charts so the entire area is shown, not a cropped part of it
  let y_extent = $derived(
    $lineChartMode === "area" ? includeZero(value_extent) : value_extent,
  );
  // Span y-axis as max minus min value plus 5 percent margin
  let y = $derived(scaleLinear([inner_height, 0]).domain(padExtent(y_extent)));

  // Quadtree for hover.
  let quad = $derived(
    quadtree(
      all_values,
      (d) => x(d.date),
      (d) => y(d.value),
    ),
  );

  let line_shape = $derived(
    line<LineChartDatum>()
      .x((d) => x(d.date))
      .y((d) => y(d.value))
      .curve(curveStepAfter),
  );

  let area_shape = $derived(
    area<LineChartDatum>()
      .x((d) => x(d.date))
      .y1((d) => y(d.value))
      .y0(Math.min(inner_height, y(0)))
      .curve(curveStepAfter),
  );

  // Axes
  let x_axis = $derived(axisBottom(x).tickSizeOuter(0));
  let y_axis = $derived(
    axisLeft(y).tickPadding(6).tickSize(-inner_width).tickFormat($short),
  );

  const tooltip_find: TooltipFindNode = (x_pointer, y_pointer) => {
    const d = quad.find(x_pointer, y_pointer);
    return d && [x(d.date), y(d.value), chart.tooltipText($ctx, d)];
  };

  let desaturate_filter_id = $derived(`desaturate-future-${uid}`);
  let desaturate_future_filter = $derived(
    x_extent[1] > today ? `url(#${desaturate_filter_id})` : undefined,
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
    {#if $lineChartMode === "area"}
      <g class="area" filter={desaturate_future_filter}>
        {#each data as d (d.name)}
          <path d={area_shape(d.values)} fill={$currenciesScale(d.name)} />
        {/each}
      </g>
    {/if}
    <g class="lines" filter={desaturate_future_filter}>
      {#each data as d (d.name)}
        <path d={line_shape(d.values)} stroke={$currenciesScale(d.name)} />
      {/each}
    </g>
    {#if $lineChartMode === "line"}
      <g>
        {#each data as d (d.name)}
          <g fill={$currenciesScale(d.name)}>
            {#each d.values as v (v.date)}
              <circle
                r="2"
                cx={x(v.date)}
                cy={y(v.value)}
                class:desaturate={v.date > today}
              />
            {/each}
          </g>
        {/each}
      </g>
    {/if}
  </Brush>
</svg>

<style>
  .lines path {
    fill: none;
    stroke-width: 2px;
  }

  .area path {
    opacity: 0.3;
  }

  .desaturate {
    filter: saturate(50%);
  }
</style>
