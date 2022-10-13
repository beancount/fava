/**
 * Helpers to update the page title.
 */

import { get as store_get } from "svelte/store";

import { getScriptTagValue } from "./lib/dom";
import { object, string } from "./lib/validation";
import { log_error } from "./log";
import router from "./router";
import { ledger_title } from "./stores";

const page_title_validator = object({
  documentTitle: string,
  pageTitle: string,
});

function setTitles(page_title: string, doc_title: string): void {
  document.title = `${doc_title} - ${store_get(ledger_title)}`;
  const pageTitle = document.querySelector("h1 strong");
  if (pageTitle) {
    // TODO: get rid of the innerHTML
    pageTitle.innerHTML = page_title;
  }
}

/**
 * Update page (next to our icon) and the html document `<title>`.
 */
export function updatePageTitle(): void {
  const v = getScriptTagValue("#page-title", page_title_validator);
  if (v.success) {
    setTitles(v.value.pageTitle, v.value.documentTitle);
  } else {
    // for frontend-rendered components, get the title.
    const { page_title } = router;
    if (page_title) {
      setTitles(page_title, page_title);
    } else {
      log_error(`Loading page title failed: ${v.value}`);
    }
  }
}
