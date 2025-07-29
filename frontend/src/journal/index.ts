import { mount, unmount } from "svelte";
import { get as store_get } from "svelte/store";

import { delegate } from "../lib/events";
import { notify_err } from "../notifications";
import { router } from "../router";
import { type SortableJournal, sortableJournal } from "../sort";
import { fql_filter } from "../stores/filters";
import { journalShow } from "../stores/journal";
import JournalFilters from "./JournalFilters.svelte";

/**
 * Escape the value to produce a valid regex for the Fava filter.
 */
export function escape_for_regex(value: string): string {
  return value.replace(/[.*+\-?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Add a filter to the existing list of filters. Any parts that are interpreted
 * as a regex must be escaped.
 */
function addFilter(value: string): void {
  const $fql_filter = store_get(fql_filter);
  router.set_search_param(
    "filter",
    $fql_filter ? `${$fql_filter} ${value}` : value,
  );
}

function handleClick({ target }: Event): void {
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
    addFilter(`payee:"^${escape_for_regex(target.innerText)}$"`);
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
    const value = `"^${escape_for_regex(target.innerText)}$"`;
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
    const entry = target.closest(".journal > li");
    if (entry) {
      entry.classList.toggle("show-full-entry");
    }
  }
}

export class FavaJournal extends HTMLElement {
  /** Unmount the Svelte component. */
  unmount?: () => void;

  /** Unsubscribe store listener. */
  unsubscribe?: () => void;

  sortableJournal?: SortableJournal;

  connectedCallback(): void {
    const ol = this.querySelector("ol");
    if (!ol) {
      throw new Error("fava-journal is missing its <ol>");
    }

    const total_pages = this.getAttribute("total-pages");
    if (total_pages != null) {
      void this.fetchAllPages(ol, parseInt(total_pages, 10));
    }

    this.unsubscribe = journalShow.subscribe((show) => {
      const classes = [...show].map((s) => `show-${s}`).join(" ");
      ol.className = `flex-table journal ${classes}`;
    });
    const component = mount(JournalFilters, { target: this, anchor: ol });
    this.unmount = () => {
      void unmount(component);
    };

    this.sortableJournal = sortableJournal(ol);
    delegate(this, "click", "li", handleClick);
  }

  disconnectedCallback(): void {
    this.unsubscribe?.();
    this.unmount?.();
  }

  async fetchAllPages(ol: HTMLOListElement, total: number): Promise<void> {
    const url = new URL(window.location.href);
    url.searchParams.set("partial", "true");

    let errorShown = false;
    const promises: Promise<NodeList | never[]>[] = [];
    for (let page = 2; page <= total; page++) {
      url.searchParams.set("page", page.toString());
      promises.push(
        fetch(url).then(async (response) => {
          if (!response.ok) {
            if (!errorShown) {
              notify_err(new Error("Failed to fetch some journal pages"));
              errorShown = true;
            }
            return [];
          }
          const html = await response.text();
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, "text/html");
          return doc.querySelectorAll("ol.journal > li:not(.head)");
        }),
      );
    }
    let sorting = false;
    for (const promise of promises) {
      ol.append(...(await promise));
      if (sorting) {
        continue;
      }
      sorting = true;
      // Batch sorting to avoid repeatedly sorting in-between consecutive
      // items appending.
      setTimeout(() => {
        sorting = false;
        if (this.sortableJournal) {
          const [column, order] = this.sortableJournal.getOrder();
          // The data is already sorted by date desc, so no need to sort again
          // if that's the current order.
          if (column !== "date" || order !== "desc") {
            this.sortableJournal.sort();
          }
        }
      });
    }
  }
}
