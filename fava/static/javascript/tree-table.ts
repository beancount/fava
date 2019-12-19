// Account trees.
//
// This handles the toggling of accounts in the accounts trees.

import { select, selectAll, delegate } from "./helpers";
import e from "./events";

e.on("page-loaded", () => {
  selectAll(".tree-table").forEach(table => {
    const expandAllLink = select(".expand-all", table);
    if (!expandAllLink) {
      return;
    }

    expandAllLink.addEventListener("click", () => {
      expandAllLink.classList.add("hidden");
      selectAll(".toggled", table).forEach(el => {
        el.classList.remove("toggled");
      });
    });

    delegate(table, "click", "span.has-children", (event: MouseEvent) => {
      if (!event.target) {
        return;
      }
      const target = event.target as HTMLElement;
      if (target.tagName === "A") {
        return;
      }
      const row = target.closest("li")!;
      const willShow = row.classList.contains("toggled");
      if (event.shiftKey) {
        selectAll("li", row).forEach(el => {
          el.classList.toggle("toggled", !willShow);
        });
      }
      if (event.ctrlKey || event.metaKey) {
        selectAll("li", row).forEach(el => {
          el.classList.toggle("toggled", willShow);
        });
      }
      row.classList.toggle("toggled");

      expandAllLink.classList.toggle(
        "hidden",
        !selectAll(".toggled", table).length
      );
    });
  });
});
