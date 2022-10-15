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
import "../css/charts.css";
import "../css/components.css";
import "../css/editor.css";
import "../css/grid.css";
import "../css/fonts.css";
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
import { initGlobalKeyboardShortcuts } from "./keyboard-shortcuts";
import { log_error } from "./log";
import { notify } from "./notifications";
import { shouldRenderInFrontend } from "./reports/routes";
import router, { setStoreValuesFromURL, syncStoreValuesToURL } from "./router";
import { initSidebar } from "./sidebar";
import { has_changes, updatePageTitle } from "./sidebar/page-title";
import { SortableTable } from "./sort";
import { errorCount, fava_options, ledgerData, rawLedgerData } from "./stores";
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

router.on("page-loaded", () => {
  rawLedgerData.set(document.getElementById("ledger-data")?.innerHTML ?? "");
  updatePageTitle();
  has_changes.set(false);
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
      has_changes.set(true);
      if (store_get(fava_options).auto_reload) {
        router.reload();
      } else {
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

  router.init(shouldRenderInFrontend);
  setStoreValuesFromURL();
  syncStoreValuesToURL();
  initSidebar();
  initGlobalKeyboardShortcuts();
  defineCustomElements();
  setInterval(doPoll, 5000);

  ledgerData.subscribe((val) => {
    errorCount.set(val.errors);
  });

  router.trigger("page-loaded");
}

init();
