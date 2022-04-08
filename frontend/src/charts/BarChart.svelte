<script lang="ts">
  import { filter, max, merge, min, sum } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { scaleBand, scaleLinear, scaleOrdinal } from "d3-scale";
  import { stack, stackOffsetDiverging } from "d3-shape";
  import type { Series } from "d3-shape";
  import { getContext } from "svelte";
  import type { Writable } from "svelte/store";

  import { ctx } from "../format";
  import { urlForAccount } from "../helpers";
  import router from "../router";
  import { barChartMode } from "../stores/chart";

  import Axis from "./Axis.svelte";
  import type { BarChart, BarChartDatum, BarChartDatumValue } from "./bar";
  import {
    currenciesScale,
    filterTicks,
    hclColorRange,
    setTimeFilter,
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
  let hasStackedData = false;

  function build_stack(_data: BarChartDatum[]) {
    const accounts = new Map<string, Series<BarChartDatum, string>[]>(
      allAccounts.map((d) => [d, []])
    );
    if (accounts.size > 1) {
      hasStackedData = true;
    }
    for (let cur_idx = 0; cur_idx < _data[0].values.length; cur_idx += 1) {
      const bar_stack = stack<BarChartDatum>()
        .keys(accounts.keys())
        .value((obj, key) => obj.values[cur_idx].children.get(key) ?? 0)
        .offset(stackOffsetDiverging)(_data);
      for (let acct_idx = 0; acct_idx < bar_stack.length; acct_idx += 1) {
        accounts.get(bar_stack[acct_idx].key)?.push(bar_stack[acct_idx]);
      }
    }
    return accounts;
  }

  $: allAccounts = Array.from(
    new Set<string>(
      data
        .map<string[]>((d: BarChartDatum) =>
          d.values
            .map<string[]>((e: BarChartDatumValue) =>
              Array.from(e.children.keys())
            )
            .flat()
        )
        .flat()
    )
  );
  $: stacked_data = build_stack(data);
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
  $: stackedBar = $barChartMode === "stacked" && hasStackedData;
  $: yMin = stackedBar
    ? min(
        merge<number>(
          data.map((b) =>
            b.values.map((c) => sum(filter(c.children.values(), (d) => d < 0)))
          )
        )
      )
    : min(merge<BarChartDatumValue>(data.map((d) => d.values)), (d) => d.value);
  $: yMax = stackedBar
    ? max(
        merge<number>(
          data.map((b) =>
            b.values.map((c) => sum(filter(c.children.values(), (d) => d > 0)))
          )
        )
      )
    : max(merge<BarChartDatumValue>(data.map((d) => d.values)), (d) => d.value);
  $: y = scaleLinear()
    .range([innerHeight, 0])
    .domain([Math.min(0, yMin ?? 0), Math.max(0, yMax ?? 0)]);

  $: colorScale = scaleOrdinal<string, string>()
    .domain(allAccounts)
    .range(hclColorRange(allAccounts.length));

  const legend: Writable<[string, string][]> = getContext("chart-legend");
  $: legend.set(
    stackedBar
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
  let highlighted = "";
</script>

<svg {width} {height}>
  <g transform={`translate(${offset},${margin.top})`}>
    <Axis x axis={xAxis} {innerHeight} />
    <Axis y axis={yAxis} />
    {#each data as group}
      <g
        class="group"
        class:desaturate={group.date > today}
        use:followingTooltip={() => tooltipText($ctx, group, "")}
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
        {#if !stackedBar}
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
        {/if}
      </g>
    {/each}
    {#if stackedBar}
      {#each [...stacked_data] as [name, account]}
        <g
          class="category"
          class:faded={name !== highlighted && highlighted !== ""}
        >
          {#each account as group, currency_idx}
            {#each group as bar}
              {#if !Number.isNaN(bar[1])}
                <rect
                  class:desaturate={bar.data.date > today}
                  width={x1.bandwidth()}
                  x={(x0(bar.data.label) ?? 0) +
                    (x1(bar.data.values[currency_idx].name) ?? 0)}
                  y={y(Math.max(bar[0], bar[1]))}
                  height={Math.abs(y(bar[1]) - y(bar[0]))}
                  fill={colorScale(name)}
                  on:mouseover={() => {
                    highlighted = name;
                  }}
                  on:focus={() => {
                    highlighted = name;
                  }}
                  on:mouseout={() => {
                    highlighted = "";
                  }}
                  on:blur={() => {
                    highlighted = "";
                  }}
                  use:followingTooltip={() => tooltipText($ctx, bar.data, name)}
                  on:click={() => {
                    if (!name.startsWith(":")) {
                      router.navigate(urlForAccount(name));
                    }
                  }}
                />
              {/if}
            {/each}
          {/each}
        </g>
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
