import { delegate } from "./lib/events";
import router from "./router";
import { SortableJournal } from "./sort";
import { fql_filter } from "./stores/filters";

/**
 * Add filter, possibly escaping it to produce a valid regex.
 */
function addFilter(value: string, escape = false): void {
  if (escape) {
    value = value.replace(/[.*+\-?^${}()|[\]\\]/g, "\\$&");
  }

  fql_filter.update((fql_filter_val) =>
    fql_filter_val ? `${fql_filter_val} ${value}` : value
  );
}

export class FavaJournal extends SortableJournal {
  constructor() {
    super();

    delegate(this, "click", "li", FavaJournal.handleClick);

    const entryButtons = document.querySelectorAll("#entry-filters button");
    // Toggle entries with buttons.
    entryButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const type = button.getAttribute("data-type");
        const shouldShow = button.classList.contains("inactive");

        button.classList.toggle("inactive", !shouldShow);
        if (
          type === "transaction" ||
          type === "custom" ||
          type === "document"
        ) {
          document
            .querySelectorAll(`#entry-filters .${type}-toggle`)
            .forEach((el) => {
              el.classList.toggle("inactive", !shouldShow);
            });
        }

        this.classList.toggle(`show-${type}`, shouldShow);

        // Modify get params
        const filterShow: string[] = [];
        entryButtons.forEach((el) => {
          const datatype = el.getAttribute("data-type");
          if (datatype && !el.classList.contains("inactive")) {
            filterShow.push(datatype);
          }
        });

        const url = new URL(window.location.href);
        url.searchParams.delete("show");
        filterShow.forEach((filter) => {
          url.searchParams.append("show", filter);
        });
        router.navigate(url.toString(), false);
      });
    });
  }

  static handleClick(event: MouseEvent): void {
    const { target } = event;
    if (
      !(target instanceof HTMLElement) ||
      target instanceof HTMLAnchorElement
    ) {
      return;
    }

    if (target.className === "tag" || target.className === "link") {
      // Filter for tags and links when clicking on them.
      addFilter(target.innerText);
    } else if (target.className === "payee") {
      // Filter for payees when clicking on them.
      // Note: any special characters in the payee string are escaped so the
      // filter matches against the payee literally.
      addFilter(`payee:"${target.innerText}"`, true);
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
  }
}
