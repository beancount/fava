<script lang="ts">
  import type { Axis } from "d3-axis";
  import type { NumberValue } from "d3-scale";
  import { select } from "d3-selection";
  import type { Action } from "svelte/action";

  type Ax = Axis<string> | Axis<NumberValue>;

  /** The d3 axis to use. */
  export let axis: Ax;
  /** True if this is an x axis. */
  export let x = false;
  /** True if this is a y axis. */
  export let y = false;
  /** Show a pronounced line at zero (for y axis). */
  export let lineAtZero: number | null = null;
  /** Height of the chart (needed for the correct offset of an x axis) */
  export let innerHeight = 0;

  $: transform = x ? `translate(0,${innerHeight.toString()})` : undefined;

  /** Svelte action to render the axis. */
  const renderAxis: Action<SVGGElement, Ax> = (node: SVGGElement, ax) => {
    const selection = select(node);
    ax(selection);

    return {
      update(new_ax) {
        new_ax(selection);
      },
    };
  };
</script>

<g class:y use:renderAxis={axis} {transform}>
  {#if y && lineAtZero !== null}
    <g class="zero" transform={`translate(0,${lineAtZero.toString()})`}>
      <line x2={-axis.tickSizeInner()} />
    </g>
  {/if}
</g>

<style>
  g :global(path),
  g :global(line) {
    fill: none;
    stroke: var(--chart-axis);
    shape-rendering: crispedges;
  }

  g.y :global(line),
  g.y :global(path.domain) {
    opacity: 0.2;
  }

  g.y .zero line {
    opacity: 1;
    stroke: #666;
  }
</style>
