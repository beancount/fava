<script lang="ts">
  import { extent, merge } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { scaleBand, scaleLinear } from "d3-scale";
  import { getContext } from "svelte";
  import type { Writable } from "svelte/store";

  import { ctx } from "../format";

  import { axis } from "./axis";
  import { currenciesScale, setTimeFilter } from "./helpers";
  import { followingTooltip } from "./tooltip";

  import type { BarChart, BarChartDatumValue } from ".";

  export let data: BarChart["data"];
  export let width: number;
  export let tooltipText: BarChart["tooltipText"];

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
  $: x0 = scaleBand()
    .padding(0.1)
    .domain(data.map((d) => d.label))
    .range([0, innerWidth]);
  $: x1 = scaleBand()
    .domain(data[0].values.map((d) => d.name))
    .range([0, x0.bandwidth()]);
  let yMin = 0;
  let yMax = 0;
  $: [yMin = 0, yMax = 0] = extent(
    merge<BarChartDatumValue>(data.map((d) => d.values)),
    (d) => d.value
  );
  $: y = scaleLinear()
    .range([innerHeight, 0])
    .domain([Math.min(0, yMin), Math.max(0, yMax)]);

  const legend: Writable<[string, string][]> = getContext("chart-legend");
  $: legend.set(
    x1
      .domain()
      .sort()
      .map((c) => [c, $currenciesScale(c)])
  );

  /**
   * Filter the ticks to have them not overlap
   */
  function filterTicks(domain: string[]) {
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
  $: yAxis = axisLeft(y).tickSize(-innerWidth).tickFormat($ctx.short);
</script>

<svg {width} {height}>
  <g transform={`translate(${offset},${margin.top})`}>
    <g
      class="x axis"
      use:axis={xAxis}
      transform={`translate(0,${innerHeight})`}
    />
    <g class="y axis" use:axis={yAxis} />
    {#each data as group}
      <g
        class="group"
        use:followingTooltip={() => tooltipText($ctx, group)}
        transform={`translate(${x0(group.label)},0)`}
      >
        <rect
          class="group-box"
          x={(x0.bandwidth() - x0.step()) / 2}
          width={x0.step()}
          height={innerHeight}
        />
        <rect
          class="axis-group-box"
          on:click={() => {
            setTimeFilter(group.date);
          }}
          transform={`translate(0,${innerHeight})`}
          width={x0.bandwidth()}
          height={margin.bottom}
        />
        {#each group.values as bar}
          <rect
            fill={$currenciesScale(bar.name)}
            width={x1.bandwidth()}
            x={x1(bar.name)}
            y={y(Math.max(0, bar.value))}
            height={Math.abs(y(bar.value) - y(0))}
          />
          <rect
            class="budget"
            width={x1.bandwidth()}
            x={x1(bar.name)}
            y={y(Math.max(0, bar.budget))}
            height={Math.abs(y(bar.budget) - y(0))}
          />
        {/each}
      </g>
    {/each}
  </g>
</svg>

<style>
  .axis-group-box {
    cursor: pointer;
    opacity: 0;
  }

  .group-box {
    opacity: 0;
  }

  .group:hover .group-box {
    opacity: 0.1;
  }

  .budget {
    opacity: 0.3;
  }
</style>
