import { pointer } from "d3-selection";
import type { Attachment } from "svelte/attachments";

/** The tooltip `<div>`, lazily created. */
const tooltip = (() => {
  let value: HTMLDivElement | null = null;
  return () => {
    if (value == null) {
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
  /** Create a <br> element. */
  br: (): HTMLBRElement => document.createElement("br"),
  /** Create a <em> element with the given content. */
  em: (content: string): HTMLElement => {
    const em = document.createElement("em");
    em.textContent = content;
    return em;
  },
  /** Create a text node for the given text. */
  t: (text: string): Text => document.createTextNode(text),
  /** Create a <pre> element with the given content. */
  pre: (content: string): HTMLPreElement => {
    const pre = document.createElement("pre");
    pre.textContent = content;
    return pre;
  },
};

export type TooltipContent = (HTMLElement | Text)[];

/**
 * Svelte attachment to have the given element act on mouse to show a tooltip.
 *
 * The tooltip will be positioned at the cursor and is given a tooltip getter
 * per <g> element.
 */
export const followingTooltip = (
  getter: () => TooltipContent,
): Attachment<SVGGElement> => {
  return (node) => {
    /** Event listener to have the tooltip follow the mouse. */
    function followMouse(event: MouseEvent) {
      const t = tooltip();
      t.style.opacity = "1";
      t.style.left = `${event.pageX.toString()}px`;
      t.style.top = `${(event.pageY - 15).toString()}px`;
    }
    const mouseenter = () => {
      const t = tooltip();
      t.replaceChildren(...getter());
    };
    node.addEventListener("mouseenter", mouseenter);
    node.addEventListener("mousemove", followMouse);
    node.addEventListener("mouseleave", hide);

    return () => {
      node.removeEventListener("mouseenter", mouseenter);
      node.removeEventListener("mousemove", followMouse);
      node.removeEventListener("mouseleave", hide);
      hide();
    };
  };
};

/** A function to find the closest node and the content to show in the tooltip. */
export type TooltipFindNode = (
  x: number,
  y: number,
) => [number, number, TooltipContent] | undefined;

/**
 * Svelte attachment to have the given <g> element act on mouse to show a tooltip.
 *
 * The parameter to the tooltip is a function that takes a position (relative
 * to the container) as input and should return the position of the tooltip,
 * i.e., the found node, again relative to the container and the desired
 * content of the tooltip.
 */
export const positionedTooltip = (
  find: TooltipFindNode,
): Attachment<SVGGElement> => {
  return (node) => {
    function mousemove(event: MouseEvent) {
      const [xPointer, yPointer] = pointer(event);
      const res = find(xPointer, yPointer);
      const matrix = node.getScreenCTM();
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
    node.addEventListener("mousemove", mousemove);
    node.addEventListener("mouseleave", hide);

    return () => {
      node.removeEventListener("mousemove", mousemove);
      node.removeEventListener("mouseleave", hide);
      hide();
    };
  };
};
