<script>
  import { max, min } from "d3-array";
  import { axisLeft, axisBottom } from "d3-axis";
  import { scaleLinear, scaleBand } from "d3-scale";
  import { getContext } from "svelte";

  import { axis } from "./axis";
  import { scales, setTimeFilter } from "./helpers";
  import { formatCurrencyShort } from "../format";
  import { followingTooltip } from "./tooltip";

  export let data;
  export let width;
  export let tooltipText;
  const maxColumnWidth = 100;
  const margin = {
    top: 10,
    right: 10,
    bottom: 30,
    left: 40,
  };
  const height = 250;
  $: innerHeight = height - margin.top - margin.bottom;
  $: maxWidth = data.length * maxColumnWidth;
  $: offset = margin.left + Math.max(0, width - maxWidth) / 2;
  $: innerWidth = Math.min(width - margin.left - margin.right, maxWidth);

  // Scales
  let x0 = scaleBand().padding(0.1);
  let x1 = scaleBand();
  let y = scaleLinear();
  $: {
    x0 = x0.range([0, innerWidth]).domain(data.map(d => d.label));
    x1 = x1.range([0, x0.bandwidth()]).domain(data[0].values.map(d => d.name));
    y = y
      .range([innerHeight, 0])
      .domain([
        Math.min(0, min(data, d => min(d.values, x => x.value)) || 0),
        Math.max(0, max(data, d => max(d.values, x => x.value)) || 0),
      ]);
  }

  const context = getContext("chart");
  $: {
    context.legend.set({
      domain: x1.domain(),
      scale: scales.currencies,
    });
  }

  function filterTicks(domain) {
    const labelsCount = innerWidth / 70;
    if (domain.length <= labelsCount) {
      return domain;
    }
    const showIndices = Math.ceil(domain.length / labelsCount);
    return domain.filter((d, i) => i % showIndices === 0);
  }

  // Axes
  $: xAxis = axisBottom(x0)
    .tickSizeOuter(0)
    .tickValues(filterTicks(x0.domain()));
  $: yAxis = axisLeft(y)
    .tickSize(-innerWidth)
    .tickFormat(formatCurrencyShort);
</script>

<svg class="barchart" {width} {height}>
  <g transform={`translate(${offset},${margin.top})`}>
    <g
      class="x axis"
      use:axis={xAxis}
      transform={`translate(0,${innerHeight})`} />
    <g class="y axis" use:axis={yAxis} />
    <g>
      {#each data as group}
        <g
          class="group"
          use:followingTooltip={() => tooltipText(group)}
          transform={`translate(${x0(group.label)},0)`}>
          <rect class="group-box" width={x0.bandwidth()} height={innerHeight} />
          <rect
            class="axis-group-box"
            on:click={() => {
              setTimeFilter(group.date);
            }}
            transform={`translate(0,${innerHeight})`}
            width={x0.bandwidth()}
            height={margin.bottom} />
          {#each group.values as bar}
            <rect
              class="bar"
              fill={scales.currencies(bar.name)}
              width={x1.bandwidth()}
              x={x1(bar.name)}
              y={y(Math.max(0, bar.value))}
              height={Math.abs(y(bar.value) - y(0))} />
          {/each}
          {#each group.values as bar}
            <rect
              class="budget"
              width={x1.bandwidth()}
              x={x1(bar.name)}
              y={y(Math.max(0, bar.budget))}
              height={Math.abs(y(bar.budget) - y(0))} />
          {/each}
        </g>
      {/each}
    </g>
  </g>
</svg>
