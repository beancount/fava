import { pointer } from "d3-selection";

/**
 * Create tooltip with accompanying hide and destroy functions.
 */
function createTooltip(): [HTMLDivElement, () => void] {
  const tooltip = document.createElement("div");
  tooltip.className = "tooltip";
  document.body.appendChild(tooltip);
  const hide = (): void => {
    tooltip.style.opacity = "0";
  };
  return [tooltip, hide];
}

const [tooltip, hide] = createTooltip();

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
  /** Event listener to have the tooltip follow the mouse. */
  function followMouse(event: MouseEvent): void {
    tooltip.style.opacity = "1";
    tooltip.style.left = `${event.pageX}px`;
    tooltip.style.top = `${event.pageY - 15}px`;
  }
  node.addEventListener("mouseenter", () => {
    tooltip.innerHTML = getter();
  });
  node.addEventListener("mousemove", followMouse);
  node.addEventListener("mouseleave", hide);

  return {
    destroy: hide,
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
    const [xPointer, yPointer] = pointer(event);
    const res = find(xPointer, yPointer);
    const matrix = node.getScreenCTM();
    if (res && matrix) {
      const [x, y, content] = res;
      tooltip.style.opacity = "1";
      tooltip.innerHTML = content;
      tooltip.style.left = `${window.scrollX + x + matrix.e}px`;
      tooltip.style.top = `${window.scrollY + y + matrix.f - 15}px`;
    } else {
      hide();
    }
  }
  node.addEventListener("mousemove", mousemove);
  node.addEventListener("mouseleave", hide);

  return {
    destroy: hide,
  };
}
