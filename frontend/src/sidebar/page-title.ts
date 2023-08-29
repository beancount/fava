/**
 * Helpers to update the page title.
 */

import { derived, writable } from "svelte/store";

import { getScriptTagValue } from "../lib/dom";
import { string } from "../lib/validation";

/** The page title, can either be the title itself or `account:{name}` */
export const raw_page_title = writable("");

/** Whether any changes to the Beancount files has been detected. */
export const has_changes = writable(false);

interface PageTitle {
  title: string;
  type: "plain" | "account";
}

export const page_title = derived(
  raw_page_title,
  ($raw_page_title): PageTitle => {
    if ($raw_page_title.startsWith("account:")) {
      return {
        title: $raw_page_title.slice("account:".length),
        type: "account",
      };
    }
    return { title: $raw_page_title, type: "plain" };
  },
);

/**
 * Update page (next to our icon) and the html document `<title>`.
 */
export function updatePageTitle(): void {
  const v = getScriptTagValue("#page-title", string);
  if (v.is_ok) {
    raw_page_title.set(v.value);
  }
}
