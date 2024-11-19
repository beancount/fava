import { mount, unmount } from "svelte";

import { delegate } from "../lib/events";
import { sortableJournal } from "../sort";
import { fql_filter } from "../stores/filters";
import { journalShow } from "../stores/journal";
import JournalFilters from "./JournalFilters.svelte";

/**
 * Escape the value to produce a valid regex for the Fava filter.
 */
export function escape(value: string): string {
  return value.replace(/[.*+\-?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Add a filter to the existing list of filters. Any parts that are interpreted
 * as a regex must be escaped.
 */
function addFilter(value: string): void {
  fql_filter.update((fql_filter_val) =>
    fql_filter_val ? `${fql_filter_val} ${value}` : value,
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
  /** Unmount the Svelte component. */
  unmount?: () => void;

  /** Unsubscribe store listener. */
  unsubscribe?: () => void;

  connectedCallback(): void {
    const ol = this.querySelector("ol");
    if (!ol) {
      throw new Error("fava-journal is missing its <ol>");
    }

    this.unsubscribe = journalShow.subscribe((show) => {
      const classes = [...show].map((s) => `show-${s}`).join(" ");
      ol.className = `flex-table journal ${classes}`;
    });
    const component = mount(JournalFilters, { target: this, anchor: ol });
    this.unmount = () => {
      void unmount(component);
    };

    sortableJournal(ol);
    delegate(this, "click", "li", handleClick);
  }

  disconnectedCallback(): void {
    this.unsubscribe?.();
    this.unmount?.();
  }
}
