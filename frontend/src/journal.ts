import { delegate } from "./lib/events";
import { log_error } from "./log";
import router from "./router";
import { sortableJournal } from "./sort";
import { fql_filter } from "./stores/filters";

/**
 * Escape the value to produce a valid regex.
 */
function escape(value: string): string {
  return value.replace(/[.*+\-?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Add a filter to the existing list of filters. Any parts that are interpreted
 * as a regex must be escaped.
 */
function addFilter(value: string): void {
  fql_filter.update((fql_filter_val) =>
    fql_filter_val ? `${fql_filter_val} ${value}` : value
  );
}

function handleClick({ target }: MouseEvent): void {
  if (!(target instanceof HTMLElement) || target instanceof HTMLAnchorElement) {
    return;
  }

  if (target.className === "tag" || target.className === "link") {
    // Filter for tags and links when clicking on them.
    addFilter(target.innerText);
  } else if (target.className === "payee") {
    // Filter for payees when clicking on them.
    // Note: any special characters in the payee string are escaped so the
    // filter matches against the payee literally.
    addFilter(`payee:"^${escape(target.innerText)}$"`);
  } else if (target.tagName === "DT") {
    // Filter for metadata key when clicking on the key. The key tag text
    // includes the colon.
    const expr = `${target.innerText}""`;
    if (target.closest(".postings")) {
      // Posting metadata.
      addFilter(`any(${expr})`);
    } else {
      // Entry metadata.
      addFilter(expr);
    }
  } else if (target.tagName === "DD") {
    // Filter for metadata key and value when clicking on the value. The key
    // tag text includes the colon.
    const key = (target.previousElementSibling as HTMLElement).innerText;
    const value = `"^${escape(target.innerText)}$"`;
    const expr = `${key}${value}`;
    if (target.closest(".postings")) {
      // Posting metadata.
      addFilter(`any(${expr})`);
    } else {
      // Entry metadata.
      addFilter(expr);
    }
  } else if (target.closest(".indicators")) {
    // Toggle postings and metadata by clicking on indicators.
    const entry = target.closest(".transaction");
    if (entry) {
      entry.classList.toggle("show-postings");
    }
  }
}

export class FavaJournal extends HTMLElement {
  constructor() {
    super();

    const ol = this.querySelector("ol");
    const form = this.querySelector("form");
    if (!ol || !form) {
      throw new Error("fava-journal is missing its <ol> or <form>");
    }
    sortableJournal(ol);
    delegate(this, "click", "li", handleClick);

    const entryButtons = form.querySelectorAll("button");
    // Toggle entries with buttons.
    entryButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const type = button.getAttribute("data-type");
        if (!type) {
          log_error("Button is missing type: ", button);
          return;
        }
        const shouldShow = button.classList.contains("inactive");

        button.classList.toggle("inactive", !shouldShow);
        if (
          type === "transaction" ||
          type === "custom" ||
          type === "document"
        ) {
          form.querySelectorAll(`.${type}-toggle`).forEach((el) => {
            el.classList.toggle("inactive", !shouldShow);
          });
        }

        ol.classList.toggle(`show-${type}`, shouldShow);

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
}
