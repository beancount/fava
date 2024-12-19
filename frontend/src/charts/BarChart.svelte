<script lang="ts">
  import { extent } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { scaleBand, scaleLinear, scaleOrdinal } from "d3-scale";

  import { urlForAccount } from "../helpers";
  import { barChartMode, chartToggledCurrencies } from "../stores/chart";
  import { ctx, currentTimeFilterDateFormat, short } from "../stores/format";
  import Axis from "./Axis.svelte";
  import type { BarChart } from "./bar";
  import {
    currenciesScale,
    filterTicks,
    hclColorRange,
    includeZero,
    padExtent,
    urlForTimeFilter,
  } from "./helpers";
  import { followingTooltip } from "./tooltip";

  interface Props {
    chart: BarChart;
    width: number;
  }

  let { chart, width }: Props = $props();

  const today = new Date();
  const maxColumnWidth = 100;
  const margin = { top: 10, right: 10, bottom: 30, left: 40 };
  const height = 250;

  let accounts = $derived(chart.accounts);

  let filtered = $derived(chart.filter($chartToggledCurrencies));
  let currencies = $derived(filtered.currencies);
  let bar_groups = $derived(filtered.bar_groups);
  let stacks = $derived(filtered.stacks);

  let innerHeight = $derived(height - margin.top - margin.bottom);
  let maxWidth = $derived(bar_groups.length * maxColumnWidth);
  let offset = $derived(margin.left + Math.max(0, width - maxWidth) / 2);
  let innerWidth = $derived(
    Math.min(width - margin.left - margin.right, maxWidth),
  );

  /** Whether to display stacked bars. */
  let showStackedBars = $derived(
    $barChartMode === "stacked" && chart.hasStackedData,
  );
  /** The currently hovered account. */
  let highlighted: string | null = $state(null);

  // Scales
  let x0 = $derived(
    scaleBand([0, innerWidth])
      .domain(bar_groups.map((d) => d.label))
      .padding(0.1),
  );
  let x1 = $derived(scaleBand([0, x0.bandwidth()]).domain(currencies));

  let yExtent = $derived(
    showStackedBars
      ? extent(stacks.flatMap(([, s]) => s.flat(2)))
      : extent(bar_groups.map((d) => d.values).flat(), (d) => d.value),
  );
  let y = $derived(
    scaleLinear([innerHeight, 0]).domain(padExtent(includeZero(yExtent))),
  );

  let colorScale = $derived(
    scaleOrdinal(hclColorRange(accounts.length)).domain(accounts),
  );

  // Axes
  let xAxis = $derived(
    axisBottom(x0)
      .tickSizeOuter(0)
      .tickValues(filterTicks(x0.domain(), innerWidth / 70)),
  );
  let yAxis = $derived(
    axisLeft(y).tickPadding(6).tickSize(-innerWidth).tickFormat($short),
  );
</script>

<svg viewBox={`0 0 ${width.toString()} ${height.toString()}`}>
  <g transform={`translate(${offset.toString()},${margin.top.toString()})`}>
    <Axis x axis={xAxis} {innerHeight} />
    <Axis y axis={yAxis} lineAtZero={y(0)} />
    {#each bar_groups as group}
      <g
        class="group"
        class:desaturate={group.date > today}
        use:followingTooltip={() => chart.tooltipText($ctx, group)}
        transform={`translate(${(x0(group.label) ?? 0).toString()},0)`}
      >
        <rect
          class="group-box"
          x={(x0.bandwidth() - x0.step()) / 2}
          width={x0.step()}
          height={innerHeight}
        />
        <a
          href={urlForTimeFilter(group.date)}
          aria-label={$currentTimeFilterDateFormat(group.date)}
        >
          <rect
            class="axis-group-box"
            transform={`translate(0,${innerHeight.toString()})`}
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
      {#each stacks as [currency, account_stacks]}
        {#each account_stacks as stack}
          {@const account = stack.key}
          <a href={$urlForAccount(account)}>
            <g
              class="category"
              class:faded={highlighted != null && account !== highlighted}
              onmouseover={() => {
                highlighted = account;
              }}
              onfocus={() => {
                highlighted = account;
              }}
              onmouseout={() => {
                highlighted = null;
              }}
              onblur={() => {
                highlighted = null;
              }}
              role="img"
            >
              {#each stack as bar}
                <rect
                  class:desaturate={bar.data.date > today}
                  width={x1.bandwidth()}
                  x={(x0(bar.data.label) ?? 0) + (x1(currency) ?? 0)}
                  y={y(Math.max(bar[0], bar[1]))}
                  height={Math.abs(y(bar[1]) - y(bar[0]))}
                  fill={colorScale(account)}
                  use:followingTooltip={() =>
                    chart.tooltipTextAccount(
                      $ctx,
                      bar.data,
                      account,
                      $chartToggledCurrencies,
                    )}
                />
              {/each}
            </g>
          </a>
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
