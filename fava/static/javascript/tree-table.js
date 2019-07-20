// Account trees.
//
// This handles the toggling of accounts in the accounts trees.

import { select, selectAll, delegate } from "./helpers";
import e from "./events";

e.on("page-loaded", () => {
  selectAll(".tree-table").forEach(table => {
    delegate(table, "click", "span.has-children", event => {
      if (event.target.tagName === "A") {
        return;
      }
      const row = event.target.closest("li");
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

      select(".expand-all", table).classList.toggle(
        "hidden",
        !selectAll(".toggled", table).length
      );
    });

    delegate(table, "click", ".expand-all", event => {
      event.target.classList.add("hidden");
      selectAll(".toggled", table).forEach(el => {
        el.classList.remove("toggled");
      });
    });
  });
});
