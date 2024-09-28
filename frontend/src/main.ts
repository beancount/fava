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
import "../css/notifications.css";
import "../css/tree-table.css";
// Polyfill for customised builtin elements in Webkit
import "@ungap/custom-elements";

import { get as store_get } from "svelte/store";

import { get } from "./api";
import { ledgerDataValidator } from "./api/validators";
import { CopyableText } from "./clipboard";
import { BeancountTextarea } from "./codemirror/setup";
import { handleExtensionPageLoad } from "./extensions";
import { _ } from "./i18n";
import { FavaJournal } from "./journal";
import { initGlobalKeyboardShortcuts } from "./keyboard-shortcuts";
import { getScriptTagValue } from "./lib/dom";
import { log_error } from "./log";
import { notify, notify_err } from "./notifications";
import { frontend_routes } from "./reports/routes";
import router, { setStoreValuesFromURL, syncStoreValuesToURL } from "./router";
import { initSidebar } from "./sidebar";
import { has_changes, updatePageTitle } from "./sidebar/page-title";
import { SortableTable } from "./sort/sortable-table";
import { errors, fava_options, ledgerData } from "./stores";
import { ledger_mtime, read_mtime } from "./stores/mtime";
import { SvelteCustomElement } from "./svelte-custom-elements";
import { TreeTableCustomElement } from "./tree-table/tree-table-custom-element";

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
  customElements.define("svelte-component", SvelteCustomElement);

  // for extension compatibility
  customElements.define("tree-table", TreeTableCustomElement);
}

router.on("page-loaded", () => {
  read_mtime();
  updatePageTitle();
  has_changes.set(false);
  handleExtensionPageLoad();
});

/**
 * Update the ledger data and errors; Reload if automatic reloading is configured.
 */
function onChanges() {
  get("ledger_data")
    .then((v) => {
      ledgerData.set(v);
    })
    .catch((e: unknown) => {
      notify_err(e, (err) => `Error fetching ledger data: ${err.message}`);
    });
  if (store_get(fava_options).auto_reload && !router.hasInteruptHandler) {
    router.reload();
  } else {
    get("errors").then((v) => {
      errors.set(v);
    }, log_error);
    notify(_("File change detected. Click to reload."), "warning", () => {
      router.reload();
    });
  }
}

/**
 * Check the `changed` API endpoint.
 *
 * Updates of the mtime returned by this endpoint will fire the appropriate events if some
 * file changed.
 *
 * This will be scheduled every 5 seconds.
 */
function pollForChanges(): void {
  get("changed").catch(log_error);
}

function init(): void {
  const initial = getScriptTagValue("#ledger-data", ledgerDataValidator);
  if (initial.is_ok) {
    ledgerData.set(initial.value);
  } else {
    log_error(initial.error);
  }
  read_mtime();

  let initial_mtime = true;
  ledger_mtime.subscribe(() => {
    if (initial_mtime) {
      initial_mtime = false;
      return;
    }
    has_changes.set(true);
    onChanges();
  });

  router.init(frontend_routes);
  setStoreValuesFromURL();
  syncStoreValuesToURL();
  initSidebar();
  initGlobalKeyboardShortcuts();
  defineCustomElements();
  setInterval(pollForChanges, 5000);

  ledgerData.subscribe((val) => {
    errors.set(val.errors);
  });

  router.trigger("page-loaded");
}

init();
