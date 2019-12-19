import { select, selectAll, delegate } from "./helpers";
import e from "./events";
import router from "./router";
import { filters } from "./stores";

function addFilter(value: string) {
  filters.update(fs => {
    if (fs.filter) {
      return {
        ...fs,
        filter: `${fs.filter} ${value}`,
      };
    }
    return {
      ...fs,
      filter: value,
    };
  });
}

e.on("page-loaded", () => {
  const journal = select(".journal");
  if (!journal) {
    return;
  }

  delegate(journal, "click", "li", event => {
    if (!event.target) {
      return;
    }
    const target = event.target as HTMLElement;
    if (target.tagName === "A") {
      return;
    }

    if (target.className === "tag" || target.className === "link") {
      // Filter for tags and links when clicking on them.
      addFilter(target.innerText);
    } else if (target.className === "payee") {
      // Filter for payees when clicking on them.
      addFilter(`payee:"${target.innerText}"`);
    } else if (target.tagName === "DD") {
      // Filter for metadata when clicking on the value.
      addFilter(
        ` ${(target.previousElementSibling as HTMLElement).innerText}"${
          target.innerText
        }"`
      );
    } else if (target.closest(".indicators")) {
      // Toggle postings and metadata by clicking on indicators.
      const entry = target.closest(".transaction");
      if (entry) {
        entry.classList.toggle("show-postings");
      }
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
      const filterShow: string[] = [];
      selectAll("#entry-filters button").forEach(el => {
        const datatype = el.getAttribute("data-type");
        if (datatype && !el.classList.contains("inactive")) {
          filterShow.push(datatype);
        }
      });

      const url = new URL(window.location.href);
      url.searchParams.delete("show");
      filterShow.forEach(filter => {
        url.searchParams.append("show", filter);
      });
      router.navigate(url.toString(), false);
    });
  });
});
