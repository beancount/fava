<script lang="ts">
  import { _ } from "../i18n";
  import type { KeySpec } from "../keyboard-shortcuts";
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import { lastActiveChartName, showCharts } from "../stores/chart";
  import type { FavaChart } from ".";
  import Chart from "./Chart.svelte";
  import ConversionAndInterval from "./ConversionAndInterval.svelte";

  export let charts: readonly FavaChart[];

  $: active_chart =
    charts.find((c) => c.name === $lastActiveChartName) ?? charts?.[0];

  // Get the shortcut key for jumping to the previous chart.
  $: shortcutPrevious = (index: number): KeySpec | undefined => {
    const current = active_chart ? charts.indexOf(active_chart) : -1;
    return index === (current - 1 + charts.length) % charts.length
      ? { key: "C", note: _("Previous") }
      : undefined;
  };
  // Get the shortcut key for jumping to the next chart.
  $: shortcutNext = (index: number): KeySpec | undefined => {
    const current = active_chart ? charts.indexOf(active_chart) : -1;
    return index === (current + 1 + charts.length) % charts.length
      ? { key: "c", note: _("Next") }
      : undefined;
  };
</script>

{#if active_chart}
  <Chart chart={active_chart}>
    <ConversionAndInterval />
  </Chart>
  <div hidden={!$showCharts}>
    {#each charts as chart, index}
      <button
        type="button"
        class="unset"
        class:selected={chart === active_chart}
        on:click={() => {
          $lastActiveChartName = chart.name;
        }}
        use:keyboardShortcut={shortcutPrevious(index)}
        use:keyboardShortcut={shortcutNext(index)}
      >
        {chart.name}
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
