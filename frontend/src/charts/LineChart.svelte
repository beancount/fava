<script>
  import { max, merge, min, extent } from "d3-array";
  import { axisLeft, axisBottom } from "d3-axis";
  import { scaleLinear, scaleUtc } from "d3-scale";
  import { quadtree } from "d3-quadtree";
  import { line, area } from "d3-shape";
  import { getContext } from "svelte";

  import { lineChartMode } from "../stores/chart";
  import { currenciesScale } from "./helpers";
  import { axis } from "./axis";
  import { formatCurrencyShort } from "../format";
  import { positionedTooltip } from "./tooltip";

  export let data;
  export let width;
  export let tooltipText;
  const margin = {
    top: 10,
    right: 10,
    bottom: 30,
    left: 40,
  };
  const height = 250;
  $: innerWidth = width - margin.left - margin.right;
  $: innerHeight = height - margin.top - margin.bottom;

  const legend = getContext("chart-legend");
  $: legend.set(
    data
      .map((d) => d.name)
      .sort()
      .map((c) => [c, $currenciesScale(c)])
  );

  // Scales
  $: allValues = merge(data.map((d) => d.values));
  $: xDomain = [
    min(data, (s) => s.values[0].date),
    max(data, (s) => s.values[s.values.length - 1].date),
  ];
  $: x = scaleUtc().domain(xDomain).range([0, innerWidth]);
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

  $: lineShape = line()
    .x((d) => x(d.date))
    .y((d) => y(d.value));

  $: areaShape = area()
    .x((d) => x(d.date))
    .y1((d) => y(d.value))
    .y0(innerHeight);

  // Axes
  $: xAxis = axisBottom(x).tickSizeOuter(0);
  $: yAxis = axisLeft(y)
    .tickPadding(6)
    .tickSize(-innerWidth)
    .tickFormat(formatCurrencyShort);

  function tooltipInfo(...pos) {
    const d = quad.find(...pos);
    return d ? [x(d.date), y(d.value), tooltipText(d)] : undefined;
  }
</script>

{#if $lineChartMode === 'line'}
  <svg class="linechart" {width} {height}>
    <g
      use:positionedTooltip={tooltipInfo}
      transform={`translate(${margin.left},${margin.top})`}>
      <g
        class="x axis"
        use:axis={xAxis}
        transform={`translate(0,${innerHeight})`} />
      <g class="y axis" use:axis={yAxis} />
      <g class="lines">
        {#each data as d}
          <path d={lineShape(d.values)} stroke={$currenciesScale(d.name)} />
        {/each}
      </g>
      <g>
        {#each data as d}
          <g fill={$currenciesScale(d.name)}>
            {#each d.values as v}
              <circle r="3" cx={x(v.date)} cy={y(v.value)} />
            {/each}
          </g>
        {/each}
      </g>
    </g>
  </svg>
{:else if $lineChartMode === 'area'}
  <svg class="areachart" {width} {height}>
    <g
      use:positionedTooltip={tooltipInfo}
      transform={`translate(${margin.left},${margin.top})`}>
      <g
        class="x axis"
        use:axis={xAxis}
        transform={`translate(0,${innerHeight})`} />
      <g class="y axis" use:axis={yAxis} />
      <g class="area">
        {#each data as d}
          <path
            d={areaShape(d.values, innerHeight)}
            fill={$currenciesScale(d.name)} />
        {/each}
      </g>
      <g class="lines">
        {#each data as d}
          <path d={lineShape(d.values)} stroke={$currenciesScale(d.name)} />
        {/each}
      </g>
    </g>
  </svg>
{/if}
