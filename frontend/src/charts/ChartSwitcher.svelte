<script lang="ts">
  import { _ } from "../i18n.ts";
  import type { KeySpec } from "../keyboard-shortcuts.ts";
  import { keyboardShortcut } from "../keyboard-shortcuts.ts";
  import { lastActiveChartName } from "../stores/chart.ts";
  import { show_charts } from "../stores/url.ts";
  import Chart from "./Chart.svelte";
  import { chartContext } from "./context.ts";
  import ConversionAndInterval from "./ConversionAndInterval.svelte";
  import type { ParsedFavaChart } from "./index.ts";

  interface Props {
    charts: readonly ParsedFavaChart[];
  }

  let { charts }: Props = $props();

  let active_chart = $derived(
    charts.find((c) => c.label === $lastActiveChartName) ?? charts[0],
  );

  // Get the shortcut key for jumping to the previous chart.
  let shortcutPrevious = $derived((index: number): KeySpec | undefined => {
    const current = active_chart ? charts.indexOf(active_chart) : -1;
    return index === (current - 1 + charts.length) % charts.length
      ? { key: "C", note: _("Previous") }
      : undefined;
  });
  // Get the shortcut key for jumping to the next chart.
  let shortcutNext = $derived((index: number): KeySpec | undefined => {
    const current = active_chart ? charts.indexOf(active_chart) : -1;
    return index === (current + 1 + charts.length) % charts.length
      ? { key: "c", note: _("Next") }
      : undefined;
  });
</script>

{#if active_chart}
  <Chart chart={active_chart.with_context($chartContext)}>
    <ConversionAndInterval />
  </Chart>
  <div hidden={!$show_charts}>
    {#each charts as chart, index (chart.label)}
      <button
        type="button"
        class="unset"
        class:selected={chart === active_chart}
        onclick={() => {
          $lastActiveChartName = chart.label;
        }}
        {@attach keyboardShortcut(shortcutPrevious(index))}
        {@attach keyboardShortcut(shortcutNext(index))}
      >
        {chart.label}
      </button>
    {/each}
  </div>
{/if}

<style>
  div {
    margin-bottom: 1.5em;
    font-size: 1em;
    color: var(--text-color-lightest);
    text-align: center;
  }

  button {
    padding: 0 0.5em;
  }

  button + button {
    border-left: 1px solid var(--text-color-lighter);
  }

  button.selected,
  button:hover {
    color: var(--text-color-lighter);
  }

  @media print {
    button {
      display: none;
      border-left: none;
    }

    button + button {
      border-left: none;
    }

    button.selected {
      display: inline;
    }
  }
</style>
