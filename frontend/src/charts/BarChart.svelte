<script lang="ts">
  import { extent } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { scaleBand, scaleLinear, scaleOrdinal } from "d3-scale";
  import { getContext } from "svelte";
  import type { Writable } from "svelte/store";

  import { urlForAccount } from "../helpers";
  import { barChartMode } from "../stores/chart";
  import { ctx } from "../stores/format";

  import Axis from "./Axis.svelte";
  import type { BarChart } from "./bar";
  import {
    currenciesScale,
    filterTicks,
    hclColorRange,
    urlForTimeFilter,
  } from "./helpers";
  import { followingTooltip } from "./tooltip";

  export let data: BarChart["data"];
  export let width: number;
  export let tooltipText: BarChart["tooltipText"];

  const today = new Date();
  const maxColumnWidth = 100;
  const margin = {
    top: 10,
    right: 10,
    bottom: 30,
    left: 40,
  };
  const height = 250;

  $: bar_groups = data.bar_groups;
  $: accounts = data.accounts;
  $: currencies = bar_groups[0]?.values.map((d) => d.currency) ?? [];

  $: innerHeight = height - margin.top - margin.bottom;
  $: maxWidth = bar_groups.length * maxColumnWidth;
  $: offset = margin.left + Math.max(0, width - maxWidth) / 2;
  $: innerWidth = Math.min(width - margin.left - margin.right, maxWidth);

  /** Whether to display stacked bars. */
  $: showStackedBars = $barChartMode === "stacked" && data.hasStackedData;
  /** The currently hovered account. */
  let highlighted: string | null = null;

  // Scales
  $: x0 = scaleBand()
    .padding(0.1)
    .domain(bar_groups.map((d) => d.label))
    .range([0, innerWidth]);
  $: x1 = scaleBand().domain(currencies).range([0, x0.bandwidth()]);

  let yMin: number;
  let yMax: number;
  $: [yMin = 0, yMax = 0] = showStackedBars
    ? extent(data.stacks.flatMap(([, s]) => s.flat(2)))
    : extent(bar_groups.map((d) => d.values).flat(), (d) => d.value);
  $: y = scaleLinear()
    .range([innerHeight, 0])
    .domain([Math.min(0, yMin), Math.max(0, yMax)]);

  $: colorScale = scaleOrdinal<string, string>()
    .domain(accounts)
    .range(hclColorRange(accounts.length));

  const legend: Writable<[string, string][]> = getContext("chart-legend");
  $: legend.set(
    showStackedBars
      ? []
      : x1
          .domain()
          .sort()
          .map((c) => [c, $currenciesScale(c)])
  );

  // Axes
  $: xAxis = axisBottom(x0)
    .tickSizeOuter(0)
    .tickValues(filterTicks(x0.domain(), innerWidth / 70));
  $: yAxis = axisLeft(y).tickSize(-innerWidth).tickFormat($ctx.short);
</script>

<svg {width} {height}>
  <g transform={`translate(${offset},${margin.top})`}>
    <Axis x axis={xAxis} {innerHeight} />
    <Axis y axis={yAxis} lineAtZero={true} />
    {#each bar_groups as group}
      <g
        class="group"
        class:desaturate={group.date > today}
        use:followingTooltip={() => tooltipText($ctx, group, "")}
        transform={`translate(${x0(group.label) ?? 0},0)`}
      >
        <rect
          class="group-box"
          x={(x0.bandwidth() - x0.step()) / 2}
          width={x0.step()}
          height={innerHeight}
        />
        <a href={urlForTimeFilter(group.date)}>
          <rect
            class="axis-group-box"
            transform={`translate(0,${innerHeight})`}
            width={x0.bandwidth()}
            height={margin.bottom}
          />
        </a>
        {#if !showStackedBars}
          {#each group.values as { currency, value, budget }}
            <rect
              fill={$currenciesScale(currency)}
              width={x1.bandwidth()}
              x={x1(currency)}
              y={y(Math.max(0, value))}
              height={Math.abs(y(value) - y(0))}
            />
            <rect
              class="budget"
              width={x1.bandwidth()}
              x={x1(currency)}
              y={y(Math.max(0, budget))}
              height={Math.abs(y(budget) - y(0))}
            />
          {/each}
        {/if}
      </g>
    {/each}
    {#if showStackedBars}
      {#each data.stacks as [currency, account_stacks]}
        {#each account_stacks as stack}
          {@const account = stack.key}
          <a href={urlForAccount(account)}>
            <g
              class="category"
              class:faded={highlighted && account !== highlighted}
            >
              {#each stack.filter((b) => !Number.isNaN(b[1])) as bar}
                <rect
                  class:desaturate={bar.data.date > today}
                  width={x1.bandwidth()}
                  x={(x0(bar.data.label) ?? 0) + (x1(currency) ?? 0)}
                  y={y(Math.max(bar[0], bar[1]))}
                  height={Math.abs(y(bar[1]) - y(bar[0]))}
                  fill={colorScale(account)}
                  on:mouseover={() => {
                    highlighted = account;
                  }}
                  on:focus={() => {
                    highlighted = account;
                  }}
                  on:mouseout={() => {
                    highlighted = null;
                  }}
                  on:blur={() => {
                    highlighted = null;
                  }}
                  use:followingTooltip={() =>
                    tooltipText($ctx, bar.data, account)}
                />
              {/each}
            </g>
          </a>v
        {/each}
      {/each}
    {/if}
  </g>
</svg>

<style>
  .category.faded {
    opacity: 0.5;
  }

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

  .desaturate {
    filter: saturate(50%);
  }
</style>
