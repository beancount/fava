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
import "codemirror/lib/codemirror.css";
import "codemirror/addon/dialog/dialog.css";
import "codemirror/addon/fold/foldgutter.css";
import "codemirror/addon/hint/show-hint.css";

// Polyfill for customised builtin elements in Webkit
import "@ungap/custom-elements";

import { get } from "./api";
import { CopyableText } from "./clipboard";
import { BeancountTextarea } from "./editor";
import { _ } from "./i18n";
import { FavaJournal } from "./journal";
import {
  initCurrentKeyboardShortcuts,
  initGlobalKeyboardShortcuts,
} from "./keyboard-shortcuts";
import { getScriptTagJSON } from "./lib/dom";
import { notify } from "./notifications";
import router, { initSyncedStoreValues } from "./router";
import { initSidebar, updateSidebar } from "./sidebar";
import { SortableTable } from "./sort";
import { errorCount, favaAPI, favaAPIStore, favaAPIValidator } from "./stores";
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

const pageTitle = document.querySelector("h1 strong");
const reloadButton = document.querySelector("#reload-page");

router.on("page-loaded", () => {
  favaAPIStore.set(favaAPIValidator(getScriptTagJSON("#ledger-data")));

  initCurrentKeyboardShortcuts();

  document.title = favaAPI.documentTitle;
  if (pageTitle) {
    pageTitle.innerHTML = favaAPI.pageTitle;
  }
  reloadButton?.classList.add("hidden");
  updateSidebar();
});

/**
 * Check the `changed` API endpoint and fire the appropriate events if some
 * file changed.
 *
 * This will be scheduled every 5 seconds.
 */
async function doPoll(): Promise<void> {
  const changed = await get("changed");
  if (changed) {
    if (favaAPI.favaOptions["auto-reload"]) {
      router.reload();
    } else {
      reloadButton?.classList.remove("hidden");
      errorCount.set(await get("errors"));
      notify(_("File change detected. Click to reload."), "warning", () => {
        router.reload();
      });
    }
  }
}

function init(): void {
  favaAPIStore.set(favaAPIValidator(getScriptTagJSON("#ledger-data")));
  router.init();
  initSyncedStoreValues();
  initSidebar();
  initGlobalKeyboardShortcuts();
  defineCustomElements();
  setInterval(doPoll, 5000);
  reloadButton?.addEventListener("click", () => {
    router.reload();
  });

  router.trigger("page-loaded");
}

init();
