/**
 * Fava's main Javascript entry point.
 *
 * The code for Fava's UI is split into several modules that are all imported
 * below. The different modules can listen to and register events to
 * communicate and to register DOM event handlers for example.
 *
 * The events currently in use in Fava:
 *
 * file-modified:
 *    Fetch and update the error count in the sidebar.
 *
 * page-init:
 *    Run once the page is initialized, i.e., when the DOM is ready. Use this
 *    for JS code and parts of the UI that are independent of the current
 *    contents of <article>.
 *
 * page-loaded:
 *    After a new page has been loaded asynchronously. Use this to bind to
 *    elements in the page.
 */

import { select, _, ready, fetchAPI, getScriptTagJSON } from "./helpers";
import e from "./events";
import router from "./router";

import "../css/style.css";
import "../css/base.css";
import "../css/charts.css";
import "../css/components.css";
import "../css/editor.css";
import "../css/entry-forms.css";
import "../css/fonts.css";
import "../css/header.css";
import "../css/help.css";
import "../css/journal-table.css";
import "../css/media-mobile.css";
import "../css/media-print.css";
import "../css/overlay.css";
import "../css/query.css";
import "../css/tree-table.css";
import "codemirror/lib/codemirror.css";
import "codemirror/addon/dialog/dialog.css";
import "codemirror/addon/fold/foldgutter.css";
import "codemirror/addon/hint/show-hint.css";

import "./charts";
import "./clipboard";
import "./editor";
import "./journal";
import "./keyboard-shortcuts";
import { notify } from "./notifications";
import "./sidebar";
import "./sort";
import "./tree-table";
import { favaAPI, favaAPIStore, favaAPIValidator } from "./stores";

import Import from "./Import.svelte";
import ChartSwitcher from "./charts/ChartSwitcher.svelte";
import FilterForm from "./FilterForm.svelte";
import Documents from "./documents/Documents.svelte";
import Modals from "./modals/Modals.svelte";
import Query from "./query/Query.svelte";

/**
 * Try to select the given element, load JSON and init Svelte component.
 *
 * On the next page load, the component will be removed.
 */
function initSvelteComponent(selector: string, SvelteComponent: any) {
  const el = select(selector);
  if (el) {
    let data = {};
    const script = select("script", el);
    if (script && (script as HTMLScriptElement).type === "application/json") {
      data = JSON.parse(script.innerHTML);
    }
    const component = new SvelteComponent({ target: el, props: { data } });
    e.once("page-loaded", () => component.$destroy());
  }
}

e.on("page-loaded", () => {
  favaAPIStore.set(favaAPIValidator(getScriptTagJSON("#ledger-data")));

  initSvelteComponent("#svelte-charts", ChartSwitcher);
  initSvelteComponent("#svelte-documents", Documents);
  initSvelteComponent("#svelte-import", Import);
  initSvelteComponent("#svelte-query", Query);

  document.title = favaAPI.documentTitle;
  select("h1 strong")!.innerHTML = favaAPI.pageTitle;
  select("#reload-page")!.classList.add("hidden");
});

e.on("page-init", () => {
  // eslint-disable-next-line no-new
  new Modals({ target: document.body });
  const header = select("header");
  if (header) {
    // eslint-disable-next-line no-new
    new FilterForm({ target: header });
  }
});

// Check the `changed` API endpoint every 5 seconds and fire the appropriate
// events if some file changed.
async function doPoll() {
  try {
    const changed = await fetchAPI("changed");
    if (changed) {
      if (favaAPI.favaOptions["auto-reload"]) {
        router.reload();
      } else {
        select("#reload-page")!.classList.remove("hidden");
        e.trigger("file-modified");
        notify(_("File change detected. Click to reload."), "warning", () => {
          router.reload();
        });
      }
    }
  } finally {
    setTimeout(doPoll, 5000);
  }
}

ready().then(() => {
  favaAPIStore.set(favaAPIValidator(getScriptTagJSON("#ledger-data")));
  router.init();
  e.trigger("page-init");
  e.trigger("page-loaded");
  setTimeout(doPoll, 5000);
});
