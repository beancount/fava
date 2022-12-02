/**
 * Helpers to update the page title.
 */

import { derived, writable } from "svelte/store";

import { getScriptTagValue } from "../lib/dom";
import { string } from "../lib/validation";

export const raw_page_title = writable("");

export const has_changes = writable(false);

interface PageTitle {
  title: string;
  type: "plain" | "account";
}

export const page_title = derived(raw_page_title, (raw): PageTitle => {
  if (raw.startsWith("account:")) {
    return { title: raw.slice("account:".length), type: "account" };
  }
  return { title: raw, type: "plain" };
});

/**
 * Update page (next to our icon) and the html document `<title>`.
 */
export function updatePageTitle(): void {
  const v = getScriptTagValue("#page-title", string);
  if (v.success) {
    raw_page_title.set(v.value);
  }
}
