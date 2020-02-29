<script>
  import { max, merge, min } from "d3-array";
  import { axisLeft, axisBottom } from "d3-axis";
  import { scaleLinear, scaleUtc } from "d3-scale";
  import { clientPoint, select } from "d3-selection";
  import { quadtree } from "d3-quadtree";
  import { line } from "d3-shape";
  import { getContext } from "svelte";

  import { scales } from "./helpers";
  import { formatCurrencyShort } from "../format";
  import { tooltip } from "./tooltip";

  export let data = [];
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

  // Elements
  let gElement;
  let xAxisElement;
  let yAxisElement;

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
  const xAxis = axisBottom(x).tickSizeOuter(0);
  let yAxis = axisLeft(y)
    .tickPadding(6)
    .tickFormat(formatCurrencyShort);
  $: yAxis = yAxis.tickSize(-innerWidth);
  $: if (x && y && yAxisElement && xAxisElement) {
    xAxis(select(xAxisElement));
    yAxis(select(yAxisElement));
  }

  // Quadtree for hover.
  $: quad = quadtree(
    merge(data.map(d => d.values)),
    d => x(d.date),
    d => y(d.value)
  );

  function mousemove(event) {
    const matrix = gElement.getScreenCTM();
    const d = quad.find(...clientPoint(gElement, event));
    if (d) {
      tooltip
        .style("opacity", 1)
        .html(tooltipText(d))
        .style("left", `${window.scrollX + x(d.date) + matrix.e}px`)
        .style("top", `${window.scrollY + y(d.value) + matrix.f - 15}px`);
    } else {
      tooltip.style("opacity", 0);
    }
  }
  function mouseleave() {
    tooltip.style("opacity", 0);
  }
</script>

<svg class="linechart" {width} {height}>
  <g
    bind:this={gElement}
    transform={`translate(${margin.left},${margin.top})`}
    on:mouseleave={mouseleave}
    on:mousemove={mousemove}>
    <g
      class="x axis"
      bind:this={xAxisElement}
      transform={`translate(0,${innerHeight})`} />
    <g class="y axis" bind:this={yAxisElement} />
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
