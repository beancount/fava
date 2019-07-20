// This script updates the links and error count in the sidebar as well as
// toggling the sidebar on mobile.

import { select, selectAll, fetchAPI } from "./helpers";
import e from "./events";

function initSidebar() {
  selectAll("aside a").forEach(el => {
    el.classList.remove("selected");
    const href = el.getAttribute("href");
    if (href && href.includes(window.location.pathname)) {
      el.classList.add("selected");
    }
  });
  const errors = select("#data-error-count").value;
  select("aside li.error").classList.toggle("hidden", errors === "0");
  select("aside li.error span").innerHTML = errors;
}

e.on("page-init", () => {
  const asideButton = select("#aside-button");
  asideButton.addEventListener("click", () => {
    select("aside").classList.toggle("active");
    asideButton.classList.toggle("active");
  });
});

e.on("page-loaded", () => {
  initSidebar();
});

e.on("file-modified", () => {
  fetchAPI("errors").then(errors => {
    select("#data-error-count").value = errors;
    initSidebar();
  });
});
