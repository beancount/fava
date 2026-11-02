<script lang="ts">
  import { _ } from "../i18n.ts";
  import type { KeySpec } from "../keyboard-shortcuts.ts";
  import { keyboard_shortcut } from "../keyboard-shortcuts.ts";
  import { set_query_param } from "../router.ts";
  import { chart_key_param, current_url, show_charts } from "../stores/url.ts";
  import Chart from "./Chart.svelte";
  import ConversionAndInterval from "./ConversionAndInterval.svelte";
  import { chart_context } from "./context.ts";
  import type { ParsedFavaChart } from "./index.ts";

  interface Props {
    charts: readonly ParsedFavaChart[];
  }

  let { charts }: Props = $props();

  const chart_key = (chart: ParsedFavaChart) => chart.key ?? chart.label;

  let active_chart = $derived(
    charts.find((c) => chart_key(c) === $chart_key_param) ?? charts[0],
  );

  // Get the link to the chart - the first chart is the default, so omit it from the URL.
  let chart_href = $derived((chart: ParsedFavaChart, index: number): string => {
    const url = new URL($current_url);
    set_query_param(url, "chart", index === 0 ? "" : (chart_key(chart) ?? ""));
    return url.toString();
  });

  // Get the shortcut key for jumping to the previous chart.
  let shortcut_previous = $derived((index: number): KeySpec | undefined => {
    const current = active_chart ? charts.indexOf(active_chart) : -1;
    return index === (current - 1 + charts.length) % charts.length
      ? { key: "C", note: _("Previous") }
      : undefined;
  });
  // Get the shortcut key for jumping to the next chart.
  let shortcut_next = $derived((index: number): KeySpec | undefined => {
    const current = active_chart ? charts.indexOf(active_chart) : -1;
    return index === (current + 1 + charts.length) % charts.length
      ? { key: "c", note: _("Next") }
      : undefined;
  });
</script>

{#if active_chart}
  <Chart chart={active_chart.with_context($chart_context)}>
    <ConversionAndInterval />
  </Chart>
  <div hidden={!$show_charts}>
    {#each charts as chart, index (chart_key(chart) ?? index)}
      <a
        href={chart === active_chart ? undefined : chart_href(chart, index)}
        class:selected={chart === active_chart}
        {@attach keyboard_shortcut(shortcut_previous(index))}
        {@attach keyboard_shortcut(shortcut_next(index))}
      >
        {chart.label}
      </a>
    {/each}
  </div>
{/if}

<style>
  div {
    margin-bottom: 1em;
    color: var(--text-color-lightest);
    text-align: center;
  }

  a {
    padding: 0 0.5em;
    color: inherit;
  }

  a + a {
    border-left: 1px solid var(--text-color-lighter);
  }

  a.selected,
  a:hover {
    color: var(--text-color-lighter);
  }

  @media print {
    a {
      display: none;
      border-left: none;
    }

    a + a {
      border-left: none;
    }

    a.selected {
      display: inline;
    }
  }
</style>
