import { clientPoint } from "d3-selection";

import e from "../events";

const tooltip = document.createElement("div");
tooltip.className = "tooltip";
document.body.appendChild(tooltip);

/** Event listener to have the tooltip follow the mouse. */
function followMouse(event: MouseEvent): void {
  tooltip.style.opacity = "1";
  tooltip.style.left = `${event.pageX}px`;
  tooltip.style.top = `${event.pageY - 15}px`;
}

/** Hide the tooltip */
function hideTooltip(): void {
  tooltip.style.opacity = "0";
}

/**
 * Svelte action to have the given element act on mouse to show a tooltip.
 *
 * The tooltip will be positioned at the cursor and is given a tooltip getter
 * per <g> element.
 */
export function followingTooltip(
  node: SVGElement,
  text: () => string
): { destroy: () => void; update: (t: () => string) => void } {
  let getter = text;
  node.addEventListener("mouseenter", () => {
    tooltip.innerHTML = getter();
  });
  node.addEventListener("mousemove", followMouse);
  node.addEventListener("mouseleave", hideTooltip);

  return {
    destroy: hideTooltip,
    update(t: () => string): void {
      getter = t;
    },
  };
}

/**
 * Svelte action to have the given <g> element act on mouse to show a tooltip.
 *
 * The parameter to the tooltip is a function that takes a position (relative
 * to the container) as input and should return the position of the tooltip,
 * i.e., the found node, again relative to the container and the desired
 * content of the tooltip.
 */
export function positionedTooltip(
  node: SVGGElement,
  find: (x: number, y: number) => [number, number, string] | undefined
): { destroy: () => void } {
  function mousemove(event: MouseEvent): void {
    const res = find(...clientPoint(node, event));
    const matrix = node.getScreenCTM();
    if (res && matrix) {
      const [x, y, content] = res;
      tooltip.style.opacity = "1";
      tooltip.innerHTML = content;
      tooltip.style.left = `${window.scrollX + x + matrix.e}px`;
      tooltip.style.top = `${window.scrollY + y + matrix.f - 15}px`;
    } else {
      hideTooltip();
    }
  }
  node.addEventListener("mousemove", mousemove);
  node.addEventListener("mouseleave", hideTooltip);

  return {
    destroy: hideTooltip,
  };
}

e.on("page-loaded", hideTooltip);
