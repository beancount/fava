<script lang="ts">
  import { extent, least } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { scaleBand, scaleLinear, scaleOrdinal } from "d3-scale";

  import { urlForAccount } from "../helpers.ts";
  import { barChartMode, chartToggledCurrencies } from "../stores/chart.ts";
  import { ctx, currentTimeFilterDateFormat, short } from "../stores/format.ts";
  import Axis from "./Axis.svelte";
  import Brush from "./Brush.svelte";
  import type { BarChart } from "./bar.ts";
  import { get_chart_tooltip } from "./context.ts";
  import {
    currenciesScale,
    filterTicks,
    hclColorRange,
    includeZero,
    padExtent,
    urlForTimeFilter,
  } from "./helpers.ts";

  interface Props {
    chart: BarChart;
    width: number;
  }

  let { chart, width }: Props = $props();

  const today = new Date();
  const tooltip = get_chart_tooltip();

  // Constant dimensions
  const max_column_width = 100;
  const margin = { top: 10, right: 10, bottom: 30, left: 40 };
  const height = 250;
  const inner_height = height - margin.top - margin.bottom;

  // Chart data
  let accounts = $derived(chart.accounts);
  let { currencies, bar_groups, stacks } = $derived(
    chart.filter($chartToggledCurrencies),
  );

  // Computed dimensions
  let max_width = $derived(bar_groups.length * max_column_width);
  let offset = $derived(margin.left + Math.max(0, width - max_width) / 2);
  let inner_width = $derived(
    Math.min(width - margin.left - margin.right, max_width),
  );

  /** Whether to display stacked bars. */
  let show_stacked_bars = $derived(
    $barChartMode === "stacked" && chart.hasStackedData,
  );

  // Scales
  let x0 = $derived(
    scaleBand([0, inner_width])
      .domain(bar_groups.map((d) => d.label))
      .padding(0.1),
  );
  let x1 = $derived(scaleBand([0, x0.bandwidth()]).domain(currencies));

  let y_extent = $derived(
    show_stacked_bars
      ? extent(stacks.flatMap(([, s]) => s.flat(2)))
      : extent(
          bar_groups.flatMap((d) => d.values),
          (d) => d.value,
        ),
  );
  let y = $derived(
    scaleLinear([inner_height, 0]).domain(padExtent(includeZero(y_extent))),
  );

  let account_color_scale = $derived(
    scaleOrdinal(hclColorRange(accounts.length)).domain(accounts),
  );

  // Axes
  let x_axis = $derived(
    axisBottom(x0)
      .tickSizeOuter(0)
      .tickValues(filterTicks(x0.domain(), inner_width / 70)),
  );
  let y_axis = $derived(
    axisLeft(y).tickPadding(6).tickSize(-inner_width).tickFormat($short),
  );

  /** Invert a pixel x position to the date of the nearest bar group. */
  function invert(px: number): Date {
    const half = x0.bandwidth() / 2;
    const closest = least(bar_groups, ({ label }) =>
      Math.abs(px - (x0(label) ?? 0) - half),
    );
    return closest?.date ?? new Date();
  }
</script>

<svg viewBox={`0 0 ${width.toString()} ${height.toString()}`}>
  <Brush
    {invert}
    height={inner_height}
    transform={`translate(${offset.toString()},${margin.top.toString()})`}
  >
    <Axis x axis={x_axis} {inner_height} />
    <Axis y axis={y_axis} line_at_zero={y(0)} />
    {#each bar_groups as group (group.date)}
      <g
        class={["group", group.date > today && "desaturate"]}
        {@attach tooltip.following(() => chart.tooltipText($ctx, group))}
        transform={`translate(${(x0(group.label) ?? 0).toString()},0)`}
      >
        <rect
          class="group-box"
          x={(x0.bandwidth() - x0.step()) / 2}
          width={x0.step()}
          height={inner_height}
        />
        <a
          href={urlForTimeFilter(group.date)}
          aria-label={$currentTimeFilterDateFormat(group.date)}
        >
          <rect
            class="axis-group-box"
            y={inner_height}
            width={x0.bandwidth()}
            height={margin.bottom}
          />
        </a>
        {#if !show_stacked_bars}
          {#each group.values as { currency, value, budget } (currency)}
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
    {#if show_stacked_bars}
      <g class="stacks">
        {#each stacks as [currency, account_stacks] (currency)}
          {#each account_stacks as stack (stack.key)}
            {@const account = stack.key}
            <a href={$urlForAccount(account)}>
              {#each stack as bar (bar.data.date)}
                <rect
                  class={[bar.data.date > today && "desaturate"]}
                  width={x1.bandwidth()}
                  x={(x0(bar.data.label) ?? 0) + (x1(currency) ?? 0)}
                  y={y(Math.max(bar[0], bar[1]))}
                  height={Math.abs(y(bar[1]) - y(bar[0]))}
                  fill={account_color_scale(account)}
                  {@attach tooltip.following(() =>
                    chart.tooltipTextAccount(
                      $ctx,
                      bar.data,
                      account,
                      $chartToggledCurrencies,
                    ),
                  )}
                />
              {/each}
            </a>
          {/each}
        {/each}
      </g>
    {/if}
  </Brush>
</svg>

<style>
  .stacks:hover a:not(:hover) {
    opacity: 0.5;
  }

  .axis-group-box,
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
