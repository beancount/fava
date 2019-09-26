/**
 * This script updates the links and error count in the sidebar as well as
 * toggling the sidebar on mobile.
 */

import { select, selectAll, fetchAPI } from "./helpers";
import { favaAPI } from "./stores";
import { number } from "./validation";
import e from "./events";

function initSidebar() {
  selectAll("aside a").forEach(el => {
    el.classList.remove("selected");
    const href = el.getAttribute("href");
    if (href && href.includes(window.location.pathname)) {
      el.classList.add("selected");
    }
  });
  select("aside li.error")!.classList.toggle("hidden", favaAPI.errors === 0);
  select("aside li.error span")!.innerHTML = `${favaAPI.errors}`;
}

e.on("page-init", () => {
  const asideButton = select("#aside-button")!;
  asideButton.addEventListener("click", () => {
    select("aside")!.classList.toggle("active");
    asideButton.classList.toggle("active");
  });
});

e.on("page-loaded", () => {
  initSidebar();
});

e.on("file-modified", async () => {
  const errors = await fetchAPI("errors");
  favaAPI.errors = number(errors);
  initSidebar();
});
