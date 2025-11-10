import { get as store_get } from "svelte/store";

import { escape_for_regex } from "../../lib/regex.ts";
import { router } from "../../router.ts";
import { fql_filter } from "../../stores/filters.ts";

/**
 * Add a filter to the existing list of filters. Any parts that are interpreted
 * as a regex must be escaped.
 */
function add_filter(value: string): void {
  const $fql_filter = store_get(fql_filter);
  router.set_search_param(
    "filter",
    $fql_filter ? `${$fql_filter} ${value}` : value,
  );
}

export function handle_journal_click({ target }: Event): void {
  if (!(target instanceof HTMLElement) || target instanceof HTMLAnchorElement) {
    return;
  }

  if (target.matches(".tag, .link")) {
    // Filter for tags and links when clicking on them.
    add_filter(target.innerText);
  } else if (target.matches(".payee")) {
    // Filter for payees when clicking on them.
    // Note: any special characters in the payee string are escaped so the
    // filter matches against the payee literally.
    add_filter(`payee:"^${escape_for_regex(target.innerText)}$"`);
  } else if (target.tagName === "DT") {
    // Filter for metadata key when clicking on the key. The key tag text
    // includes the colon.
    const expr = `${target.innerText}""`;
    add_filter(target.closest(".postings") ? `any(${expr})` : expr);
  } else if (target.tagName === "DD") {
    // Filter for metadata key and value when clicking on the value. The key
    // tag text includes the colon.
    const key = (target.previousElementSibling as HTMLElement).innerText;
    const value = `"^${escape_for_regex(target.innerText)}$"`;
    const expr = `${key}${value}`;
    add_filter(target.closest(".postings") ? `any(${expr})` : expr);
  } else if (target.closest(".indicators")) {
    // Toggle postings and metadata by clicking on indicators.
    target.closest(".journal > li")?.classList.toggle("show-full-entry");
  }
}
