import { pointer } from "d3-selection";

/** The tooltip div, lazily created. */
const tooltip = (() => {
  let value: HTMLDivElement | null = null;
  return () => {
    if (value === null) {
      value = document.createElement("div");
      value.className = "tooltip";
      document.body.appendChild(value);
    }
    return value;
  };
})();

/** Hide the tooltip. */
const hide = (): void => {
  const t = tooltip();
  t.style.opacity = "0";
};

/** Some small utilities to create tooltip contents. */
export const domHelpers = {
  br: () => document.createElement("br"),
  em: (content: string) => {
    const em = document.createElement("em");
    em.textContent = content;
    return em;
  },
  t: (text: string) => document.createTextNode(text),
};

export type TooltipContent = (HTMLElement | Text)[];

/**
 * Svelte action to have the given element act on mouse to show a tooltip.
 *
 * The tooltip will be positioned at the cursor and is given a tooltip getter
 * per <g> element.
 */
export function followingTooltip(
  node: SVGElement,
  text: () => TooltipContent
): { destroy: () => void; update: (t: () => TooltipContent) => void } {
  let getter = text;
  /** Event listener to have the tooltip follow the mouse. */
  function followMouse(event: MouseEvent): void {
    const t = tooltip();
    t.style.opacity = "1";
    t.style.left = `${event.pageX}px`;
    t.style.top = `${event.pageY - 15}px`;
  }
  node.addEventListener("mouseenter", () => {
    const t = tooltip();
    t.replaceChildren(...getter());
  });
  node.addEventListener("mousemove", followMouse);
  node.addEventListener("mouseleave", hide);

  return {
    destroy: hide,
    update(t: () => TooltipContent): void {
      getter = t;
    },
  };
}

/** A function to find the closest node and the content to show in the tooltip. */
export type TooltipFindNode = (
  x: number,
  y: number
) => [number, number, TooltipContent] | undefined;

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
  find: TooltipFindNode
): { destroy: () => void } {
  function mousemove(event: MouseEvent): void {
    const [xPointer, yPointer] = pointer(event);
    const res = find(xPointer, yPointer);
    const matrix = node.getScreenCTM();
    if (res && matrix) {
      const [x, y, content] = res;
      const t = tooltip();
      t.style.opacity = "1";
      t.replaceChildren(...content);
      t.style.left = `${window.scrollX + x + matrix.e}px`;
      t.style.top = `${window.scrollY + y + matrix.f - 15}px`;
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
