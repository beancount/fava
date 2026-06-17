<!--
  @component
  A `<g>` wrapper for a brush for a horizontal time selection by dragging.

  Can show a positioned tooltip by providing a find function.
-->
<script lang="ts">
  import { pointer } from "d3-selection";
  import type { Snippet } from "svelte";
  import type { SVGAttributes } from "svelte/elements";

  import { router } from "../router.ts";
  import { currentTimeFilterDateFormat } from "../stores/format.ts";
  import { hide, type TooltipFindNode, tooltip } from "./tooltip.ts";

  /** Ignore tiny drags less than 5px. */
  const DRAG_THRESHOLD = 5;

  interface Props extends Pick<SVGAttributes<SVGGElement>, "transform"> {
    /** Function to invert an x position to its date. */
    invert: (px: number) => Date;
    /** Height of the `<g>`. */
    height: number;
    /** Optional content for a following tooltip to show. */
    find?: TooltipFindNode;
    children: Snippet;
  }

  let { invert, height, children, find, transform }: Props = $props();

  let x_start = $state(0);
  let x_current = $state(0);
  let active_pointer_id = $state<number>();

  let active = $derived(
    active_pointer_id != null && Math.abs(x_current - x_start) > DRAG_THRESHOLD,
  );

  function onpointerdown(event: PointerEvent) {
    if (
      active_pointer_id != null ||
      event.button !== 0 ||
      event.ctrlKey ||
      event.metaKey ||
      event.shiftKey
    ) {
      return;
    }
    [x_start] = pointer(event);
    x_current = x_start;
    active_pointer_id = event.pointerId;
    event.preventDefault();
  }

  function onpointermove(event: PointerEvent & { currentTarget: SVGGElement }) {
    const [x_pointer, y_pointer] = pointer(event);
    if (find != null) {
      const res = find(x_pointer, y_pointer);
      const matrix = event.currentTarget.getScreenCTM();
      if (res && matrix) {
        const [x, y, content] = res;
        const t = tooltip();
        t.style.opacity = "1";
        t.replaceChildren(...content);
        t.style.left = `${(window.scrollX + x + matrix.e).toString()}px`;
        t.style.top = `${(window.scrollY + y + matrix.f - 15).toString()}px`;
      } else {
        hide();
      }
    }
    if (event.pointerId !== active_pointer_id) {
      return;
    }
    x_current = x_pointer;
  }

  function onpointerup(event: PointerEvent) {
    if (event.pointerId !== active_pointer_id) {
      return;
    }
    if (active) {
      const [x_end] = pointer(event);
      const start_date = invert(Math.min(x_start, x_end));
      const end_date = invert(Math.max(x_start, x_end));
      const start = $currentTimeFilterDateFormat(start_date);
      const end = $currentTimeFilterDateFormat(end_date);
      const time_filter = start === end ? start : `${start} - ${end}`;
      router.set_search_param("time", time_filter);
    }
    active_pointer_id = undefined;
  }

  function onpointerleave() {
    // Cancel when leaving the container element
    active_pointer_id = undefined;
    hide();
  }
</script>

<g
  class={{ active }}
  role="application"
  {transform}
  {onpointerdown}
  {onpointermove}
  {onpointerleave}
  {onpointerup}
>
  {@render children()}
  {#if active}
    <rect
      x={Math.min(x_start, x_current)}
      y="0"
      {height}
      width={Math.abs(x_current - x_start)}
    />
  {/if}
</g>

<style>
  g {
    pointer-events: all;
    touch-action: pan-y pinch-zoom;
  }

  g.active {
    cursor: ew-resize;
  }

  rect {
    opacity: 0.1;
    fill: var(--text-color);
  }
</style>
