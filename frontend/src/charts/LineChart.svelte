<script lang="ts">
  import { extent, max, merge, min } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { quadtree } from "d3-quadtree";
  import { scaleLinear, scaleUtc } from "d3-scale";
  import { area, curveStepAfter, line } from "d3-shape";
  import { getContext } from "svelte";
  import type { Writable } from "svelte/store";

  import { lineChartMode } from "../stores/chart";
  import { ctx } from "../stores/format";

  import Axis from "./Axis.svelte";
  import { currenciesScale } from "./helpers";
  import type { LineChart, LineChartDatum } from "./line";
  import type { TooltipFindNode } from "./tooltip";
  import { positionedTooltip } from "./tooltip";

  export let data: LineChart["data"];
  export let width: number;
  export let tooltipText: LineChart["tooltipText"];

  const today = new Date();
  const margin = {
    top: 10,
    right: 10,
    bottom: 30,
    left: 40,
  };
  const height = 250;
  $: innerWidth = width - margin.left - margin.right;
  $: innerHeight = height - margin.top - margin.bottom;

  const legend: Writable<[string, string][]> = getContext("chart-legend");
  $: legend.set(
    data
      .map((d) => d.name)
      .sort()
      .map((c) => [c, $currenciesScale(c)])
  );

  // Scales
  $: allValues = merge<LineChartDatum>(data.map((d) => d.values));

  let xDomain: [Date, Date];
  $: xDomain = [
    min(data, (s) => s.values[0]?.date) ?? today,
    max(data, (s) => s.values[s.values.length - 1]?.date) ?? today,
  ];
  $: x = scaleUtc().domain(xDomain).range([0, innerWidth]);
  let yMin: number;
  let yMax: number;
  $: [yMin = 0, yMax = 0] = extent(allValues, (v) => v.value);
  // Span y-axis as max minus min value plus 5 percent margin
  $: y = scaleLinear()
    .domain([yMin - (yMax - yMin) * 0.05, yMax + (yMax - yMin) * 0.05])
    .range([innerHeight, 0]);

  // Quadtree for hover.
  $: quad = quadtree(
    allValues,
    (d) => x(d.date),
    (d) => y(d.value)
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
    .tickFormat($ctx.short);

  const tooltipFindNode: TooltipFindNode = (xPos, yPos) => {
    const d = quad.find(xPos, yPos);
    return d && [x(d.date), y(d.value), tooltipText($ctx, d)];
  };

  $: futureFilter = xDomain[1] > today ? "url(#desaturateFuture)" : undefined;
</script>

<svg {width} {height}>
  <filter id="desaturateFuture">
    <feColorMatrix type="saturate" values="0.5" x={x(today)} />
    <feBlend in2="SourceGraphic" />
  </filter>
  <g
    use:positionedTooltip={tooltipFindNode}
    transform={`translate(${margin.left},${margin.top})`}
  >
    <Axis x axis={xAxis} {innerHeight} />
    <Axis y axis={yAxis} />
    {#if $lineChartMode === "area"}
      <g class="area" filter={futureFilter}>
        {#each data as d}
          <path
            d={areaShape(d.values) ?? undefined}
            fill={$currenciesScale(d.name)}
          />
        {/each}
      </g>
    {/if}
    <g class="lines" filter={futureFilter}>
      {#each data as d}
        <path
          d={lineShape(d.values) ?? undefined}
          stroke={$currenciesScale(d.name)}
        />
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
