/**
 * Fava's main Javascript entry point.
 *
 * The code for Fava's UI is split into several modules that are all imported
 * below. The most interactive parts are written as Svelte components. Some
 * other functionality is written in plain Javascript and or web components
 * extending normal HTML elements.
 */

import "../css/style.css";
import "../css/base.css";
import "../css/layout.css";
import "../css/aside.css";
import "../css/charts.css";
import "../css/components.css";
import "../css/editor.css";
import "../css/grid.css";
import "../css/fonts.css";
import "../css/header.css";
import "../css/help.css";
import "../css/journal-table.css";
import "../css/media-mobile.css";
import "../css/media-print.css";
import "../css/notifications.css";
import "../css/tree-table.css";

// Polyfill for customised builtin elements in Webkit
import "@ungap/custom-elements";
import { get as store_get } from "svelte/store";

import { get } from "./api";
import { CopyableText } from "./clipboard";
import { BeancountTextarea } from "./codemirror/setup";
import { _ } from "./i18n";
import { FavaJournal } from "./journal";
import {
  initCurrentKeyboardShortcuts,
  initGlobalKeyboardShortcuts,
} from "./keyboard-shortcuts";
import { getScriptTagJSON } from "./lib/dom";
import { object, string } from "./lib/validation";
import { log_error } from "./log";
import { notify } from "./notifications";
import router, { initSyncedStoreValues } from "./router";
import { initSidebar, updateSidebar } from "./sidebar";
import { SortableTable } from "./sort";
import { errorCount, favaOptions, ledgerData, rawLedgerData } from "./stores";
import { SvelteCustomElement } from "./svelte-custom-elements";
import { TreeTable } from "./tree-table";

/**
 * Define the custom elements that Fava uses.
 */
function defineCustomElements() {
  customElements.define("beancount-textarea", BeancountTextarea, {
    extends: "textarea",
  });
  customElements.define("copyable-text", CopyableText);
  customElements.define("fava-journal", FavaJournal);
  customElements.define("sortable-table", SortableTable, { extends: "table" });
  customElements.define("tree-table", TreeTable);
  customElements.define("svelte-component", SvelteCustomElement);
}

const pageTitleValidator = object({
  documentTitle: string,
  pageTitle: string,
});

function updatePageTitle(): void {
  const v = pageTitleValidator(getScriptTagJSON("#page-title"));
  document.title = v.documentTitle;
  const pageTitle = document.querySelector("h1 strong");
  if (pageTitle) {
    pageTitle.innerHTML = v.pageTitle;
  }
}

router.on("page-loaded", () => {
  rawLedgerData.set(document.getElementById("ledger-data")?.innerHTML ?? "");
  updatePageTitle();
  initCurrentKeyboardShortcuts();
  document.getElementById("reload-page")?.classList.add("hidden");
  updateSidebar();
});

/**
 * Check the `changed` API endpoint and fire the appropriate events if some
 * file changed.
 *
 * This will be scheduled every 5 seconds.
 */
function doPoll(): void {
  get("changed").then((changed) => {
    if (changed) {
      if (store_get(favaOptions)["auto-reload"]) {
        router.reload();
      } else {
        document.getElementById("reload-page")?.classList.remove("hidden");
        get("errors").then((count) => errorCount.set(count), log_error);
        notify(_("File change detected. Click to reload."), "warning", () => {
          router.reload();
        });
      }
    }
  }, log_error);
}

function init(): void {
  rawLedgerData.set(document.getElementById("ledger-data")?.innerHTML ?? "");

  router.init();
  initSyncedStoreValues();
  initSidebar();
  initGlobalKeyboardShortcuts();
  defineCustomElements();
  setInterval(doPoll, 5000);
  document.getElementById("reload-page")?.addEventListener("click", () => {
    router.reload();
  });

  ledgerData.subscribe((val) => {
    errorCount.set(val.errors);
  });

  router.trigger("page-loaded");
}

init();
