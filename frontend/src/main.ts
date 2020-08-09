/**
 * Fava's main Javascript entry point.
 *
 * The code for Fava's UI is split into several modules that are all imported
 * below. The most interactive parts are written as Svelte components. Some
 * other functionality is written in plain Javascript and or web components
 * extending normal HTML elements.
 */

import { SvelteComponentDev } from "svelte/internal";

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

import { _ } from "./i18n";
import router, { initSyncedStoreValues } from "./router";
import { CopyableSpan } from "./clipboard";
import { BeancountTextarea } from "./editor";
import { FavaJournal } from "./journal";
import {
  initCurrentKeyboardShortcuts,
  initGlobalKeyboardShortcuts,
} from "./keyboard-shortcuts";
import { notify } from "./notifications";
import { updateSidebar, AsideButton, ErrorCount } from "./sidebar";
import { SortableTable } from "./sort";
import { TreeTable } from "./tree-table";
import { favaAPI, favaAPIStore, favaAPIValidator, errorCount } from "./stores";

import Editor from "./editor/Editor.svelte";
import Import from "./import/Import.svelte";
import ChartSwitcher from "./charts/ChartSwitcher.svelte";
import FilterForm from "./FilterForm.svelte";
import Documents from "./documents/Documents.svelte";
import Modals from "./modals/Modals.svelte";
import Query from "./query/Query.svelte";
import { getScriptTagJSON } from "./lib/dom";
import { get } from "./api";

customElements.define("aside-button", AsideButton, { extends: "button" });
customElements.define("beancount-textarea", BeancountTextarea, {
  extends: "textarea",
});
customElements.define("error-count", ErrorCount, { extends: "li" });
customElements.define("copyable-span", CopyableSpan, { extends: "span" });
customElements.define("fava-journal", FavaJournal, { extends: "ol" });
customElements.define("sortable-table", SortableTable, { extends: "table" });
customElements.define("tree-table", TreeTable, { extends: "ol" });

/**
 * Try to select the given element, load JSON and init Svelte component.
 *
 * On the next page load, the component will be removed.
 */
function initSvelteComponent(
  selector: string,
  SvelteComponent: typeof SvelteComponentDev
): void {
  const el = document.querySelector(selector);
  if (el) {
    const props: { data?: unknown } = {};
    const script = el.querySelector("script");
    if (script && script.type === "application/json") {
      props.data = JSON.parse(script.innerHTML);
    }
    const component = new SvelteComponent({ target: el, props });
    router.once("before-page-loaded", () => component.$destroy());
  }
}

const pageTitle = document.querySelector("h1 strong");
const reloadButton = document.querySelector("#reload-page");
router.on("page-loaded", () => {
  favaAPIStore.set(favaAPIValidator(getScriptTagJSON("#ledger-data")));

  router.once("before-page-loaded", initCurrentKeyboardShortcuts());
  initSvelteComponent("#svelte-charts", ChartSwitcher);
  initSvelteComponent("#svelte-documents", Documents);
  initSvelteComponent("#svelte-editor", Editor);
  initSvelteComponent("#svelte-import", Import);
  initSvelteComponent("#svelte-query", Query);

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
  // eslint-disable-next-line no-new
  new Modals({ target: document.body });
  const header = document.querySelector("header");
  if (header) {
    // eslint-disable-next-line no-new
    new FilterForm({ target: header });
  }
  initGlobalKeyboardShortcuts();
  setInterval(doPoll, 5000);
  reloadButton?.addEventListener("click", () => {
    router.reload();
  });

  router.trigger("page-loaded");
}

init();
