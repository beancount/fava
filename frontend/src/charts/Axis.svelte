<script lang="ts">
  import type { Axis } from "d3-axis";
  import { select } from "d3-selection";

  /** The d3 axis to use. */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  export let axis: Axis<any>;
  /** True if this is an x axis. */
  export let x = false;
  /** True if this is a y axis. */
  export let y = false;
  /** Whether to show a more pronounced line at zero (for y axis). */
  export let lineAtZero = false;
  /** Height of the chart (needed for the correct offset of an x axis) */
  export let innerHeight = 0;

  $: transform = x ? `translate(0,${innerHeight})` : undefined;

  /** Svelte action to render the axis. */
  function use(
    node: SVGGElement,
    ax: Axis<unknown>
  ): { update: (a: Axis<unknown>) => void } {
    const selection = select(node);
    ax(selection);

    return {
      update(a) {
        a(selection);
      },
    };
  }
</script>

<g class:y use:use={axis} {transform}>
  {#if y && lineAtZero}
    <g class="zero" transform={`translate(0,${axis.scale()(0) ?? 0})`}>
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
