import type { Attachment } from "svelte/attachments";
import { get as store_get } from "svelte/store";

import { router } from "../router.ts";
import { currentTimeFilterDateFormat } from "../stores/format.ts";

const DRAG_THRESHOLD = 2;

/**
 * Create a Svelte attachment that adds horizontal brush selection to a chart.
 *
 * @param invert - Function to convert a pixel x position to a Date.
 * @param innerWidth - The width of the chart area.
 * @param innerHeight - The height of the chart area.
 */
export function dateRangeBrush(
  invert: (px: number) => Date,
  innerWidth: number,
  innerHeight: number,
): Attachment<SVGGElement> {
  return (node) => {
    let startX = 0;
    let activePointerId: number | null = null;
    let rect: SVGRectElement | null = null;

    // Prevent touch scrolling so the brush works on touch devices.
    node.style.touchAction = "none";

    function localX(event: PointerEvent): number {
      const ctm = node.getScreenCTM();
      if (!ctm) {
        return 0;
      }
      return Math.max(0, Math.min((event.clientX - ctm.e) / ctm.a, innerWidth));
    }

    function onPointerDown(event: PointerEvent) {
      if (
        activePointerId != null ||
        event.button !== 0 ||
        event.ctrlKey ||
        event.metaKey ||
        event.shiftKey
      ) {
        return;
      }
      startX = localX(event);
      activePointerId = event.pointerId;
      event.preventDefault();
    }

    function onPointerMove(event: PointerEvent) {
      if (event.pointerId !== activePointerId) {
        return;
      }
      const currentX = localX(event);
      if (!rect) {
        if (Math.abs(currentX - startX) <= DRAG_THRESHOLD) {
          return;
        }
        node.setPointerCapture(event.pointerId);
        rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rect.setAttribute("y", "0");
        rect.setAttribute("height", innerHeight.toString());
        rect.style.fill = "var(--text-color)";
        rect.style.opacity = "0.1";
        node.appendChild(rect);
        document.body.style.cursor = "ew-resize";
      }
      rect.setAttribute("x", Math.min(startX, currentX).toString());
      rect.setAttribute("width", Math.abs(currentX - startX).toString());
    }

    function onPointerUp(event: PointerEvent) {
      if (event.pointerId !== activePointerId) {
        return;
      }
      if (rect) {
        const endX = localX(event);
        const date1 = invert(Math.min(startX, endX));
        const date2 = invert(Math.max(startX, endX));
        const fmt = store_get(currentTimeFilterDateFormat);
        const start = fmt(date1);
        const end = fmt(date2);
        router.set_search_param(
          "time",
          start === end ? start : `${start} - ${end}`,
        );
        document.body.style.cursor = "";
        rect.remove();
        rect = null;
      }
      activePointerId = null;
    }

    node.addEventListener("pointerdown", onPointerDown);
    node.addEventListener("pointermove", onPointerMove);
    node.addEventListener("pointerup", onPointerUp);

    return () => {
      node.removeEventListener("pointerdown", onPointerDown);
      node.removeEventListener("pointermove", onPointerMove);
      node.removeEventListener("pointerup", onPointerUp);
      document.body.style.cursor = "";
      rect?.remove();
    };
  };
}
