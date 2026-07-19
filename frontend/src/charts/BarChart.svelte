<script lang="ts">
  import { extent, least } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import type { NumberValue } from "d3-scale";
  import { scaleBand, scaleLinear, scaleOrdinal } from "d3-scale";

  import { urlForAccount } from "../helpers.ts";
  import { barChartMode, chartToggledCurrencies } from "../stores/chart.ts";
  import {
    ctx,
    currentTimeFilterDateFormat,
    plainNum,
    short,
  } from "../stores/format.ts";
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
    separateMarkerPositions,
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
  const min_visible_bar_height = 2;

  // Chart data
  let accounts = $derived(chart.accounts);
  let all_currencies = $derived(chart.currencies);
  let {
    currencies: visible_currencies,
    bar_groups,
    averages: filtered_averages,
    stacks,
  } = $derived(chart.filter($chartToggledCurrencies));
  let averages = $derived(filtered_averages ?? {});
  let has_averages = $derived(Object.keys(averages).length > 0);

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
  let x1 = $derived(scaleBand([0, x0.bandwidth()]).domain(all_currencies));

  let y_values = $derived(
    show_stacked_bars
      ? [...stacks.flatMap(([, s]) => s.flat(2)), ...Object.values(averages)]
      : [
          ...bar_groups.flatMap((d) => d.values.map((v) => v.value)),
          ...Object.values(averages),
        ],
  );
  let y_extent = $derived(extent(y_values));
  let y = $derived(
    scaleLinear([inner_height, 0]).domain(padExtent(includeZero(y_extent))),
  );
  let y_tick_format = $derived((value: NumberValue) =>
    has_averages ? $plainNum(Number(value)) : $short(value),
  );
  let average_markers = $derived.by(() => {
    const entries = visible_currencies
      .map((currency) => ({
        currency,
        value: averages[currency],
      }))
      .filter(
        (
          entry,
        ): entry is {
          currency: string;
          value: number;
        } => entry.value != null,
      );
    const marker_positions = separateMarkerPositions(
      entries.map(({ value }) => y(value)),
      8,
      0,
      inner_height,
    );
    return entries.map(({ currency, value }, index) => ({
      currency,
      value,
      line_y: y(value),
      marker_y: marker_positions[index] ?? y(value),
    }));
  });

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
    axisLeft(y).tickPadding(6).tickSize(-inner_width).tickFormat(y_tick_format),
  );

  /** Invert a pixel x position to the date of the nearest bar group. */
  function invert(px: number): Date {
    const half = x0.bandwidth() / 2;
    const closest = least(bar_groups, ({ label }) =>
      Math.abs(px - (x0(label) ?? 0) - half),
    );
    return closest?.date ?? new Date();
  }

  function barHeight(start: number, end = 0): number {
    const height = Math.abs(y(start) - y(end));
    return start !== end && height < min_visible_bar_height
      ? min_visible_bar_height
      : height;
  }

  function isTinyBar(value: number): boolean {
    return value !== 0 && Math.abs(y(value) - y(0)) < min_visible_bar_height;
  }
</script>

{#if has_averages}
  <div class="averages">
    {#each visible_currencies as currency (currency)}
      {#if averages[currency] != null}
        <span
          class="average"
          style={`--average-color:${$currenciesScale(currency)};`}
          title={currency}
        >
          <span class="dot"></span>
          <span class="label">{currency}</span>
          <span class="value"
            >{$ctx.amount(averages[currency] ?? 0, currency)}</span
          >
        </span>
      {/if}
    {/each}
  </div>
{/if}

<svg viewBox={`0 0 ${width.toString()} ${height.toString()}`}>
  <Brush
    {invert}
    height={inner_height}
    transform={`translate(${offset.toString()},${margin.top.toString()})`}
  >
    <Axis x axis={x_axis} {inner_height} />
    <Axis y axis={y_axis} line_at_zero={y(0)} />
    {#if has_averages}
      <g class="average-lines">
        {#each average_markers as { currency, line_y, marker_y } (currency)}
          <g transform={`translate(0,${line_y.toString()})`}>
            <line
              class="average-line"
              x2={inner_width}
              stroke={$currenciesScale(currency)}
            />
          </g>
          <path
            class="average-marker-connector"
            d={`M ${Math.max(inner_width - 14, 0).toString()} ${line_y.toString()} L ${(inner_width + 4).toString()} ${marker_y.toString()}`}
            stroke={$currenciesScale(currency)}
          />
          <circle
            class="average-marker"
            cx={inner_width + 4}
            cy={marker_y}
            r="3"
            fill={$currenciesScale(currency)}
          />
        {/each}
      </g>
    {/if}
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
              height={barHeight(value)}
            />
            <rect
              class="budget"
              width={x1.bandwidth()}
              x={x1(currency)}
              y={y(Math.max(0, budget))}
              height={barHeight(budget)}
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
                  height={barHeight(bar[1], bar[0])}
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
      <g class="tiny-bar-markers">
        {#each bar_groups as group (group.date)}
          {#each group.values as { currency, value } (currency)}
            {#if isTinyBar(value)}
              <rect
                class="tiny-bar-marker"
                width={x1.bandwidth()}
                x={(x0(group.label) ?? 0) + (x1(currency) ?? 0)}
                y={y(Math.max(0, value))}
                height={min_visible_bar_height}
                fill={$currenciesScale(currency)}
              />
            {/if}
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

  .averages {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5em;
    margin: 0 0 0.5em;
  }

  .average {
    display: inline-flex;
    gap: 0.35em;
    align-items: center;
    padding: 0.2em 0.45em;
    font-size: 0.85em;
    color: var(--text-color);
    background: var(--background);
    border: 1px solid var(--border-darker);
    border-radius: 0.25em;
  }

  .average .dot {
    flex: 0 0 auto;
    width: 0.6em;
    height: 0.6em;
    background: var(--average-color);
    border-radius: 999px;
  }

  .average .label {
    font-weight: 600;
  }

  .average .value {
    color: var(--text-color-lightest);
  }

  .average-lines {
    pointer-events: none;
  }

  .average-line {
    opacity: 0.9;
    stroke-width: 1.5px;
    stroke-dasharray: 4 4;
  }

  .average-marker-connector,
  .average-marker {
    opacity: 0.9;
    stroke-width: 1.5px;
  }

  .average-marker-connector {
    fill: none;
  }

  .average-marker {
    stroke: var(--background);
    stroke-width: 1px;
  }

  .tiny-bar-markers {
    pointer-events: none;
  }

  .tiny-bar-marker {
    opacity: 0.9;
  }

  .desaturate {
    filter: saturate(50%);
  }
</style>
