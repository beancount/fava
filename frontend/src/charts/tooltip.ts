import type { Attachment } from "svelte/attachments";

/** A tooltip, a light wrapper around a `<div>` in a chart container. */
export class Tooltip {
  private div: HTMLDivElement;

  constructor() {
    this.div = document.createElement("div");
    this.div.className = "tooltip top";
    this.div.hidden = true;
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
    let min_left = 0;
    let max_right = document.documentElement.clientWidth;
    const article = this.div.closest("article");
    if (article) {
      const rect = article.getBoundingClientRect();
      const client_left = rect.left + article.clientLeft;
      min_left = Math.max(min_left, client_left);
      max_right = Math.min(max_right, client_left + article.clientWidth);
    }
    const width = max_right - min_left;
    if (width <= 0) {
      this.hide();
      return;
    }
    this.div.style.setProperty("--tooltip-max-width", `${width.toString()}px`);
    this.div.hidden = false;
    this.div.style.left = `${Math.round(left).toString()}px`;
    this.div.style.top = `${Math.round(top).toString()}px`;
    const rect = this.div.getBoundingClientRect();
    const shift = Math.max(
      min_left - rect.left,
      Math.min(max_right - rect.right, 0),
    );
    this.div.style.setProperty("--tooltip-shift", `${shift.toString()}px`);
    this.div.style.left = `${(Math.round(left) + shift).toString()}px`;
  }

  /** Hide the tooltip. */
  hide(): void {
    this.div.hidden = true;
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

/**
 * A function to find the closest node to the pointer.
 *
 * Returns the position of the node, the node itself, and a function to create
 * the content to show in the tooltip for it.
 */
export type TooltipFindNode = (
  x_pointer: number,
  y_pointer: number,
) =>
  | [x: number, y: number, node: unknown, content: () => TooltipContent]
  | undefined;
