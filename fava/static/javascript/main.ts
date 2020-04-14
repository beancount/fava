/**
 * Fava's main Javascript entry point.
 *
 * The code for Fava's UI is split into several modules that are all imported
 * below. The different modules can listen to and register events to
 * communicate and to register DOM event handlers for example.
 *
 * The events currently in use in Fava:
 *
 * page-init:
 *    Run once the page is initialized. Use this for JS code and parts of the
 *    UI that are independent of the current contents of <article>.
 *
 * page-loaded:
 *    After a new page has been loaded asynchronously. Use this to bind to
 *    elements in the page.
 */

import { SvelteComponentDev } from "svelte/internal";

import "../css/style.css";
import "../css/base.css";
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

import { select, _, fetchAPI, getScriptTagJSON } from "./helpers";
import e from "./events";
import router from "./router";
import { CopyableSpan } from "./clipboard";
import { BeancountTextarea } from "./editor";
import { FavaJournal } from "./journal";
import "./keyboard-shortcuts";
import { notify } from "./notifications";
import { updateSidebar, AsideButton, ErrorCount } from "./sidebar";
import { SortableTable } from "./sort";
import { TreeTable } from "./tree-table";
import {
  favaAPI,
  favaAPIStore,
  favaAPIValidator,
  fetchErrorCount,
} from "./stores";

import Editor from "./editor/Editor.svelte";
import Import from "./import/Import.svelte";
import ChartSwitcher from "./charts/ChartSwitcher.svelte";
import FilterForm from "./FilterForm.svelte";
import Documents from "./documents/Documents.svelte";
import Modals from "./modals/Modals.svelte";
import Query from "./query/Query.svelte";

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
  const el = select(selector);
  if (el) {
    const props: { data?: unknown } = {};
    const script = el.querySelector("script");
    if (script && script.type === "application/json") {
      props.data = JSON.parse(script.innerHTML);
    }
    const component = new SvelteComponent({ target: el, props });
    e.once("before-page-loaded", () => component.$destroy());
  }
}

const pageTitle = select("h1 strong");
e.on("page-loaded", () => {
  favaAPIStore.set(favaAPIValidator(getScriptTagJSON("#ledger-data")));

  initSvelteComponent("#svelte-charts", ChartSwitcher);
  initSvelteComponent("#svelte-documents", Documents);
  initSvelteComponent("#svelte-editor", Editor);
  initSvelteComponent("#svelte-import", Import);
  initSvelteComponent("#svelte-query", Query);

  document.title = favaAPI.documentTitle;
  if (pageTitle) {
    pageTitle.innerHTML = favaAPI.pageTitle;
  }
  select("#reload-page")?.classList.add("hidden");
  updateSidebar();
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
async function doPoll(): Promise<void> {
  try {
    const changed = await fetchAPI("changed");
    if (changed) {
      if (favaAPI.favaOptions["auto-reload"]) {
        router.reload();
      } else {
        select("#reload-page")?.classList.remove("hidden");
        fetchErrorCount();
        notify(_("File change detected. Click to reload."), "warning", () => {
          router.reload();
        });
      }
    }
  } finally {
    setTimeout(doPoll, 5000);
  }
}

favaAPIStore.set(favaAPIValidator(getScriptTagJSON("#ledger-data")));
router.init();
e.trigger("page-init");
e.trigger("page-loaded");
setTimeout(doPoll, 5000);
