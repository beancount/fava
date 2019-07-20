import { select, selectAll, delegate } from "./helpers";
import e from "./events";
import router from "./router";
import { filters } from "./stores";

function addFilter(value) {
  filters.update(fs => {
    if (fs.filter) {
      fs.filter += ` ${value}`;
    } else {
      fs.filter = value;
    }
    return fs;
  });
}

e.on("page-loaded", () => {
  const journal = select(".journal");
  if (!journal) return;

  delegate(journal, "click", "li", event => {
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
        ` ${event.target.previousElementSibling.innerText}"${event.target.innerText}"`
      );
    } else if (event.target.closest(".indicators")) {
      // Toggle postings and metadata by clicking on indicators.
      const transaction = event.target.closest(".transaction");
      transaction.classList.toggle("show-postings");
    }
  });

  // Toggle entries with buttons.
  selectAll("#entry-filters button").forEach(button => {
    button.addEventListener("click", () => {
      const type = button.getAttribute("data-type");
      const shouldShow = button.classList.contains("inactive");

      button.classList.toggle("inactive", !shouldShow);
      if (type === "transaction" || type === "custom" || type === "document") {
        selectAll(`#entry-filters .${type}-toggle`).forEach(el => {
          el.classList.toggle("inactive", !shouldShow);
        });
      }

      journal.classList.toggle(`show-${type}`, shouldShow);

      // Modify get params
      const filterShow = [];
      selectAll("#entry-filters button").forEach(el => {
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
