// This script updates the links and error count in the sidebar as well as
// toggling the sidebar on mobile.

import { $, $$, fetchAPI } from "./helpers";
import e from "./events";

function initSidebar() {
  $$("aside a").forEach(el => {
    el.classList.remove("selected");
    if (el.getAttribute("href").startsWith(window.location.pathname)) {
      el.classList.add("selected");
    }
  });
  const errors = $("#data-error-count").value;
  $("aside li.error").classList.toggle("hidden", errors === "0");
  $("aside li.error span").innerHTML = errors;
}

e.on("button-click-toggle-aside", button => {
  $("aside").classList.toggle("active");
  button.classList.toggle("active");
});

e.on("page-loaded", () => {
  initSidebar();
});

e.on("file-modified", () => {
  fetchAPI("errors").then(errors => {
    $("#data-error-count").value = errors;
    initSidebar();
  });
});
