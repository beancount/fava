import e from "./events";
import { timeFilterDateFormat } from "./format";
import { $, $$ } from "./helpers";

// Adjust the size of the input element.
function updateInput(input) {
  const size = Math.max(
    input.value.length,
    input.getAttribute("placeholder").length
  );
  input.setAttribute("size", size + 1);

  const isEmpty = !input.value;
  input.closest("span").classList.toggle("empty", isEmpty);
}

export default function setTimeFilter(date) {
  const interval = $("#chart-interval").value;
  const input = $("#time-filter");
  input.value = timeFilterDateFormat[interval](date);
  updateInput(input);
  e.trigger("form-submit-filters", input.form);
}

e.on("page-loaded", () => {
  ["account", "filter", "time"].forEach(filter => {
    const value = new URLSearchParams(window.location.search).get(filter);
    const el = document.getElementById(`${filter}-filter`);
    if (value) {
      el.value = value;
    }
    updateInput(el);
  });
});

e.on("page-init", () => {
  $$("#filter-form input").forEach(input => {
    input.addEventListener("autocomplete-select", () => {
      updateInput(input);
      e.trigger("form-submit-filters", input.form);
    });

    input.addEventListener("input", () => {
      updateInput(input);
    });
  });
});

e.on("button-click-filter-clear", button => {
  const input = $("input", button.closest("span"));
  input.value = "";
  updateInput(input);
  if (new URLSearchParams(window.location.search).get(input.name)) {
    e.trigger("form-submit-filters", button.form);
  }
});
