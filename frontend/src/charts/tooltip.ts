import type { Attachment } from "svelte/attachments";

/** The tooltip `<div>`, lazily created. */
export const tooltip = (() => {
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
export const hide = (): void => {
  const t = tooltip();
  t.style.opacity = "0";
};

/** Some small utilities to create tooltip contents. */
export const domHelpers = {
  /** Create a <br> element. */
  br: () => document.createElement("br"),
  /** Create a <em> element with the given content. */
  em: (content) => {
    const em = document.createElement("em");
    em.textContent = content;
    return em;
  },
} satisfies Record<string, (x: string) => HTMLElement>;

export type TooltipContent = (HTMLElement | string)[];

/**
 * Svelte attachment to have the given element act on mouse to show a tooltip.
 *
 * The tooltip will be positioned at the cursor and is given a tooltip getter
 * per element.
 */
export const followingTooltip = (
  getter: () => TooltipContent,
): Attachment<SVGElement> => {
  return (node) => {
    const mouseenter = () => {
      const t = tooltip();
      t.replaceChildren(...getter());
    };
    function mousemove(event: MouseEvent) {
      const t = tooltip();
      t.style.opacity = "1";
      t.style.left = `${event.pageX.toString()}px`;
      t.style.top = `${(event.pageY - 15).toString()}px`;
    }
    node.addEventListener("mouseenter", mouseenter);
    node.addEventListener("mousemove", mousemove);
    node.addEventListener("mouseleave", hide);

    return () => {
      node.removeEventListener("mouseenter", mouseenter);
      node.removeEventListener("mousemove", mousemove);
      node.removeEventListener("mouseleave", hide);
      hide();
    };
  };
};

/** A function to find the closest node and the content to show in the tooltip. */
export type TooltipFindNode = (
  x_pointer: number,
  y_pointer: number,
) => [number, number, TooltipContent] | undefined;
