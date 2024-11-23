<script lang="ts">
  import { extent, max, min } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { quadtree } from "d3-quadtree";
  import { scaleLinear, scaleUtc } from "d3-scale";
  import { area, curveStepAfter, line } from "d3-shape";

  import { chartToggledCurrencies, lineChartMode } from "../stores/chart";
  import { ctx, short } from "../stores/format";
  import Axis from "./Axis.svelte";
  import { currenciesScale, includeZero, padExtent } from "./helpers";
  import type { LineChart, LineChartDatum } from "./line";
  import type { TooltipFindNode } from "./tooltip";
  import { positionedTooltip } from "./tooltip";

  interface Props {
    chart: LineChart;
    width: number;
  }

  let { chart, width }: Props = $props();

  const today = new Date();
  const margin = { top: 10, right: 10, bottom: 30, left: 40 };
  const height = 250;
  let innerWidth = $derived(width - margin.left - margin.right);
  let innerHeight = $derived(height - margin.top - margin.bottom);

  let data = $derived(chart.filter($chartToggledCurrencies));

  // Scales and quadtree
  let allValues = $derived(data.map((d) => d.values).flat(1));

  let xExtent = $derived([
    min(data, (s) => s.values[0]?.date) ?? today,
    max(data, (s) => s.values[s.values.length - 1]?.date) ?? today,
  ] as const);
  let x = $derived(scaleUtc([0, innerWidth]).domain(xExtent));
  let valueExtent = $derived(extent(allValues, (v) => v.value));
  // Include zero in area charts so the entire area is shown, not a cropped part of it
  let yExtent = $derived(
    $lineChartMode === "area" ? includeZero(valueExtent) : valueExtent,
  );
  // Span y-axis as max minus min value plus 5 percent margin
  let y = $derived(scaleLinear([innerHeight, 0]).domain(padExtent(yExtent)));

  // Quadtree for hover.
  let quad = $derived(
    quadtree(
      allValues,
      (d) => x(d.date),
      (d) => y(d.value),
    ),
  );

  let lineShape = $derived(
    line<LineChartDatum>()
      .x((d) => x(d.date))
      .y((d) => y(d.value))
      .curve(curveStepAfter),
  );

  let areaShape = $derived(
    area<LineChartDatum>()
      .x((d) => x(d.date))
      .y1((d) => y(d.value))
      .y0(Math.min(innerHeight, y(0)))
      .curve(curveStepAfter),
  );

  // Axes
  let xAxis = $derived(axisBottom(x).tickSizeOuter(0));
  let yAxis = $derived(
    axisLeft(y).tickPadding(6).tickSize(-innerWidth).tickFormat($short),
  );

  const tooltipFindNode: TooltipFindNode = (xPos, yPos) => {
    const d = quad.find(xPos, yPos);
    return d && [x(d.date), y(d.value), chart.tooltipText($ctx, d)];
  };

  let futureFilter = $derived(
    xExtent[1] > today ? "url(#desaturateFuture)" : undefined,
  );
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
