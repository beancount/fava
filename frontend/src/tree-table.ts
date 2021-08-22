import { delegate } from "./lib/events";

/**
 * Account trees.
 *
 * This handles the toggling of accounts in the accounts trees.
 */
export class TreeTable extends HTMLElement {
  constructor() {
    super();

    const expandAllLink = this.querySelector(".expand-all");
    expandAllLink?.addEventListener("click", () => {
      expandAllLink.classList.add("hidden");
      this.querySelectorAll(".toggled").forEach((el) => {
        el.classList.remove("toggled");
      });
    });

    delegate(this, "click", "span.has-children", (event: MouseEvent) => {
      const { target } = event;
      if (
        !(target instanceof HTMLElement) ||
        target instanceof HTMLAnchorElement
      ) {
        return;
      }
      const row = target.closest("li");
      if (!row) {
        return;
      }
      const willShow = row.classList.contains("toggled");
      if (event.shiftKey) {
        this.querySelectorAll("li").forEach((el) => {
          el.classList.toggle("toggled", !willShow);
        });
      }
      if (event.ctrlKey || event.metaKey) {
        this.querySelectorAll("li").forEach((el) => {
          el.classList.toggle("toggled", willShow);
        });
      }
      row.classList.toggle("toggled");

      expandAllLink?.classList.toggle(
        "hidden",
        !this.querySelectorAll(".toggled").length
      );
    });
  }
}
