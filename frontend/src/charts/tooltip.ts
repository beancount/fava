import type { Attachment } from "svelte/attachments";

/** A tooltip, a light wrapper around a `<div>` that's added to the `<body>` */
export class Tooltip {
  private div: HTMLDivElement;

  constructor() {
    this.div = document.createElement("div");
    this.div.className = "tooltip top";
  }

  init(node: HTMLElement): void {
    node.appendChild(this.div);
  }

  /** Set the tooltip content. */
  content(nodes: (Node | string)[]): void {
    this.div.replaceChildren(...nodes);
  }

  /** Position the tooltip. */
  position(left: number, top: number): void {
    this.div.style.opacity = "1";
    this.div.style.left = `${Math.round(left).toString()}px`;
    this.div.style.top = `${Math.round(top).toString()}px`;
  }

  /** Hide the tooltip. */
  hide(): void {
    this.div.style.opacity = "0";
  }

  /**
   * Svelte attachment to have the given element act on mouse to show a tooltip.
   *
   * The tooltip will be positioned at the cursor and is given a tooltip getter
   * per element.
   */
  following(getter: () => (Node | string)[]): Attachment<SVGElement> {
    return (node) => {
      const mouseenter = () => {
        this.content(getter());
      };
      const mousemove = (event: MouseEvent) => {
        this.position(event.offsetX, event.offsetY);
      };
      const hide = this.hide.bind(this);

      node.addEventListener("mouseenter", mouseenter);
      node.addEventListener("mousemove", mousemove);
      node.addEventListener("mouseleave", hide);

      return () => {
        node.removeEventListener("mouseenter", mouseenter);
        node.removeEventListener("mousemove", mousemove);
        node.removeEventListener("mouseleave", hide);
      };
    };
  }
}

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

/** A function to find the closest node and the content to show in the tooltip. */
export type TooltipFindNode = (
  x_pointer: number,
  y_pointer: number,
) => [number, number, TooltipContent] | undefined;
