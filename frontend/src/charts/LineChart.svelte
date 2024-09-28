<script lang="ts">
  import { extent, max, min } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { quadtree } from "d3-quadtree";
  import { scaleLinear, scaleUtc } from "d3-scale";
  import { area, curveStepAfter, line } from "d3-shape";
  import type { Writable } from "svelte/store";

  import { chartToggledCurrencies, lineChartMode } from "../stores/chart";
  import { ctx, short } from "../stores/format";
  import Axis from "./Axis.svelte";
  import { currenciesScale, includeZero, padExtent } from "./helpers";
  import type { LineChart, LineChartDatum } from "./line";
  import type { TooltipFindNode } from "./tooltip";
  import { positionedTooltip } from "./tooltip";

  export let chart: LineChart;
  export let width: number;
  export let legend: Writable<[string, string | null][]>;

  const today = new Date();
  const margin = { top: 10, right: 10, bottom: 30, left: 40 };
  const height = 250;
  $: innerWidth = width - margin.left - margin.right;
  $: innerHeight = height - margin.top - margin.bottom;

  $: data = chart.filter($chartToggledCurrencies);
  $: series_names = chart.series_names;

  $: legend.set(series_names.map((c) => [c, $currenciesScale(c)]));

  // Scales and quadtree
  $: allValues = data.map((d) => d.values).flat(1);

  $: xExtent = [
    min(data, (s) => s.values[0]?.date) ?? today,
    max(data, (s) => s.values[s.values.length - 1]?.date) ?? today,
  ] as const;
  $: x = scaleUtc([0, innerWidth]).domain(xExtent);
  $: valueExtent = extent(allValues, (v) => v.value);
  // Include zero in area charts so the entire area is shown, not a cropped part of it
  $: yExtent =
    $lineChartMode === "area" ? includeZero(valueExtent) : valueExtent;
  // Span y-axis as max minus min value plus 5 percent margin
  $: y = scaleLinear([innerHeight, 0]).domain(padExtent(yExtent));

  // Quadtree for hover.
  $: quad = quadtree(
    allValues,
    (d) => x(d.date),
    (d) => y(d.value),
  );

  $: lineShape = line<LineChartDatum>()
    .x((d) => x(d.date))
    .y((d) => y(d.value))
    .curve(curveStepAfter);

  $: areaShape = area<LineChartDatum>()
    .x((d) => x(d.date))
    .y1((d) => y(d.value))
    .y0(Math.min(innerHeight, y(0)))
    .curve(curveStepAfter);

  // Axes
  $: xAxis = axisBottom(x).tickSizeOuter(0);
  $: yAxis = axisLeft(y)
    .tickPadding(6)
    .tickSize(-innerWidth)
    .tickFormat($short);

  const tooltipFindNode: TooltipFindNode = (xPos, yPos) => {
    const d = quad.find(xPos, yPos);
    return d && [x(d.date), y(d.value), chart.tooltipText($ctx, d)];
  };

  $: futureFilter = xExtent[1] > today ? "url(#desaturateFuture)" : undefined;
</script>

<svg viewBox={`0 0 ${width.toString()} ${height.toString()}`}>
  <filter id="desaturateFuture">
    <feColorMatrix type="saturate" values="0.5" x={x(today)} />
    <feBlend in2="SourceGraphic" />
  </filter>
  <g
    use:positionedTooltip={tooltipFindNode}
    transform={`translate(${margin.left.toString()},${margin.top.toString()})`}
  >
    <Axis x axis={xAxis} {innerHeight} />
    <Axis y axis={yAxis} />
    {#if $lineChartMode === "area"}
      <g class="area" filter={futureFilter}>
        {#each data as d}
          <path d={areaShape(d.values)} fill={$currenciesScale(d.name)} />
        {/each}
      </g>
    {/if}
    <g class="lines" filter={futureFilter}>
      {#each data as d}
        <path d={lineShape(d.values)} stroke={$currenciesScale(d.name)} />
      {/each}
    </g>
    {#if $lineChartMode === "line"}
      <g>
        {#each data as d}
          <g fill={$currenciesScale(d.name)}>
            {#each d.values as v}
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
  </g>
</svg>

<style>
  svg > g {
    pointer-events: all;
  }

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
