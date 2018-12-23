import { $, $$ } from "./helpers";
import e from "./events";
import router from "./router";

function addFilter(value) {
  const filter = $("#filter-filter");
  if (filter.value) {
    filter.value += ` ${value}`;
  } else {
    filter.value = value;
  }
  e.trigger("form-submit-filters", filter.form);
}

e.on("page-loaded", () => {
  const journal = $("#journal-table");
  if (!journal) return;

  $.delegate(journal, "click", "li", event => {
    if (event.target.tagName === "A") {
      return;
    }

    if (event.target.className === "tag" || event.target.className === "link") {
      // Filter for tags and links when clicking on them.
      addFilter(event.target.innerText);
    } else if (event.target.className === "payee") {
      // Filter for payees when clicking on them.
      addFilter(`payee:"${event.target.innerText}"`);
    } else if (event.target.tagName === "DD") {
      // Filter for metadata when clicking on the value.
      addFilter(
        ` ${event.target.previousElementSibling.innerText}"${
          event.target.innerText
        }"`
      );
    } else if (event.target.closest(".indicators")) {
      // Toggle postings and metadata by clicking on indicators.
      const transaction = event.target.closest(".transaction");
      transaction.classList.toggle("show-postings");
    }
  });

  // Toggle entries with buttons.
  $$("#entry-filters button").forEach(button => {
    button.addEventListener("click", () => {
      const type = button.getAttribute("data-type");
      const shouldShow = button.classList.contains("inactive");

      button.classList.toggle("inactive", !shouldShow);
      if (type === "transaction" || type === "custom" || type === "document") {
        $$(`#entry-filters .${type}-toggle`).forEach(el => {
          el.classList.toggle("inactive", !shouldShow);
        });
      }

      journal.classList.toggle(`show-${type}`, shouldShow);

      // Modify get params
      const filterShow = [];
      $$("#entry-filters button").forEach(el => {
        if (!el.classList.contains("inactive")) {
          filterShow.push(el.getAttribute("data-type"));
        }
      });

      const url = new URL(window.location);
      url.searchParams.delete("show");
      filterShow.forEach(filter => {
        url.searchParams.append("show", filter);
      });
      router.navigate(url.toString(), false);
    });
  });
});
