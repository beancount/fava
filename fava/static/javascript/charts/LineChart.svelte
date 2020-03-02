<script>
  import { max, merge, min } from "d3-array";
  import { axisLeft, axisBottom } from "d3-axis";
  import { scaleLinear, scaleUtc } from "d3-scale";
  import { quadtree } from "d3-quadtree";
  import { line } from "d3-shape";
  import { getContext } from "svelte";

  import { scales } from "./helpers";
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

  const context = getContext("chart");
  $: if (data) {
    context.legend.set({
      domain: data.map(d => d.name),
      scale: scales.currencies,
    });
  }

  // Scales
  let x = scaleUtc();
  let y = scaleLinear();
  $: {
    x = x.range([0, innerWidth]);
    y = y.range([innerHeight, 0]);
  }
  $: {
    x = x.domain([
      min(data, s => s.values[0].date) || 0,
      max(data, s => s.values[s.values.length - 1].date) || 0,
    ]);

    // Span y-axis as max minus min value plus 5 percent margin
    const minDataValue = min(data, d => min(d.values, v => v.value));
    const maxDataValue = max(data, d => max(d.values, v => v.value));
    if (minDataValue !== undefined && maxDataValue !== undefined) {
      y = y.domain([
        minDataValue - (maxDataValue - minDataValue) * 0.05,
        maxDataValue + (maxDataValue - minDataValue) * 0.05,
      ]);
    }
  }

  $: lineShape = line()
    .x(d => x(d.date))
    .y(d => y(d.value));

  // Axes
  $: xAxis = axisBottom(x).tickSizeOuter(0);
  $: yAxis = axisLeft(y)
    .tickPadding(6)
    .tickSize(-innerWidth)
    .tickFormat(formatCurrencyShort);

  // Quadtree for hover.
  $: quad = quadtree(
    merge(data.map(d => d.values)),
    d => x(d.date),
    d => y(d.value)
  );

  function tooltipInfo(...pos) {
    const d = quad.find(...pos);
    return d ? [x(d.date), y(d.value), tooltipText(d)] : undefined;
  }
</script>

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
        <path d={lineShape(d.values)} stroke={scales.currencies(d.name)} />
      {/each}
    </g>
    <g>
      {#each data as d}
        <g fill={scales.currencies(d.name)}>
          {#each d.values as v}
            <circle r="3" cx={x(v.date)} cy={y(v.value)} />
          {/each}
        </g>
      {/each}
    </g>
  </g>
</svg>
