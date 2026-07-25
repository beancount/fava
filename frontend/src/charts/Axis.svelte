<!--
  @component
  A chart axis (for either an x or y axis).
-->
<script lang="ts">
  import type { Axis } from "d3-axis";
  import type { NumberValue } from "d3-scale";
  import { select } from "d3-selection";

  type Ax = Axis<string> | Axis<NumberValue>;

  interface Props {
    /** The d3 axis to use. */
    axis: Ax;
    /** True if this is an x axis. */
    x?: boolean;
    /** True if this is a y axis. */
    y?: boolean;
    /** Show a pronounced line at zero (for y axis). */
    line_at_zero?: number;
    /** Height of the chart (needed for the correct offset of an x axis). */
    inner_height?: number;
  }

  let {
    axis,
    x = false,
    y = false,
    line_at_zero,
    inner_height = 0,
  }: Props = $props();

  let transform = $derived(
    x ? `translate(0,${inner_height.toString()})` : undefined,
  );
</script>

<g
  class:y
  {transform}
  {@attach (node: SVGGElement) => {
    const selection = select(node);

    $effect(() => {
      axis(selection);
    });
  }}
>
  {#if y && line_at_zero != null}
    <g class="zero" transform={`translate(0,${line_at_zero.toString()})`}>
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
    stroke: var(--chart-line-at-zero);
  }
</style>
