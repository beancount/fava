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
import { ledgerDataValidator } from "./api/validators";
import { CopyableText } from "./clipboard";
import { BeancountTextarea } from "./codemirror/setup";
import { urlFor } from "./helpers";
import { _ } from "./i18n";
import { FavaJournal } from "./journal";
import { initGlobalKeyboardShortcuts } from "./keyboard-shortcuts";
import { getScriptTagValue } from "./lib/dom";
import { log_error } from "./log";
import { notify, notify_err } from "./notifications";
import { shouldRenderInFrontend } from "./reports/routes";
import router, { setStoreValuesFromURL, syncStoreValuesToURL } from "./router";
import { initSidebar } from "./sidebar";
import { has_changes, updatePageTitle } from "./sidebar/page-title";
import { SortableTable } from "./sort";
import { errors, fava_options, ledgerData } from "./stores";
import { ledger_mtime, read_mtime } from "./stores/mtime";
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

interface ExtensionModule {
  onExtensionInit?: (this: ExtensionModule) => void;
  onExtensionPageLoad?: (this: ExtensionModule) => void;
}

declare global {
  interface Window {
    extension?: ExtensionModule;
  }
}

/**
 * Class to wrap an individual extension module and handle calling module functions
 */
class Extension {
  extension_name: string;

  extension_module: ExtensionModule;

  constructor(extension_name: string, extension_module: ExtensionModule) {
    this.extension_name = extension_name;
    this.extension_module = extension_module;
  }

  initExtension(): void {
    if (this.extension_module.onExtensionInit) {
      this.extension_module.onExtensionInit();
    }
  }

  onPageLoad(): void {
    if (this.extension_module.onExtensionPageLoad) {
      this.extension_module.onExtensionPageLoad();
    }
  }
}

const extensions: Extension[] = [];

/**
 * On page load, check if the new page is an extension report page,
 * and update the window.extension property. If it is an extension page,
 * notify the extension module of the page load.
 */
function handleExtensionPageLoad() {
  const paths = window.location.pathname.split("/");
  window.extension = undefined;
  if (paths.length > 3 && paths[2] === "extension") {
    for (const ext of extensions) {
      if (paths[3] === ext.extension_name) {
        window.extension = ext.extension_module;
        ext.onPageLoad();
      }
    }
  }
}

router.on("page-loaded", () => {
  read_mtime();
  updatePageTitle();
  has_changes.set(false);
  handleExtensionPageLoad();
});

/**
 * Check the `changed` API endpoint and fire the appropriate events if some
 * file changed.
 *
 * This will be scheduled every 5 seconds.
 */
function pollForChanges(): void {
  get("changed").then((changed) => {
    if (changed) {
      has_changes.set(true);
      if (store_get(fava_options).auto_reload) {
        router.reload();
      } else {
        get("errors").then((v) => errors.set(v), log_error);
        notify(_("File change detected. Click to reload."), "warning", () => {
          router.reload();
        });
      }
    }
  }, log_error);
}

interface ModuleImport {
  default?: ExtensionModule;
}

/**
 * Check the extension_modules endpoint to get a list of extension modules
 * to load dynamically. Load and initialize each of these modules and trigger
 * the "page-loaded" event once everything is loaded.
 */
function initExtensions(extension_modules: string[]): void {
  const module_promises = extension_modules.map(async (name) => {
    const extension_module: ModuleImport = await (import(
      urlFor(`extension_js_module/${name}.js`, undefined, false)
    ) as Promise<ModuleImport>);
    if (typeof extension_module.default === "object") {
      return new Extension(name, extension_module.default);
    }
    throw new Error(
      `Error importing module for extension ${name}: module must export "default" object`
    );
  });
  Promise.allSettled(module_promises)
    .then((extensionResults) => {
      for (const res of extensionResults) {
        if (res.status === "fulfilled") {
          res.value.initExtension();
          extensions.push(res.value);
        } else {
          log_error(res.reason);
        }
      }
      router.trigger("page-loaded");
    })
    .catch(log_error);
}

function init(): void {
  const initial = getScriptTagValue("#ledger-data", ledgerDataValidator);
  if (initial.success) {
    ledgerData.set(initial.value);
  } else {
    log_error(initial.value);
  }
  read_mtime();

  let initial_mtime = true;
  ledger_mtime.subscribe(() => {
    if (initial_mtime) {
      initial_mtime = false;
      return;
    }
    get("ledger_data")
      .then((v) => {
        ledgerData.set(v);
      })
      .catch((e) => {
        notify_err(e, (err) => `Error fetching ledger data: ${err.message}`);
      });
  });

  router.init(shouldRenderInFrontend);
  setStoreValuesFromURL();
  syncStoreValuesToURL();
  initSidebar();
  initGlobalKeyboardShortcuts();
  defineCustomElements();
  setInterval(pollForChanges, 5000);

  ledgerData.subscribe((val) => {
    errors.set(val.errors);
    initExtensions(val.extension_js_modules);
  });
}

init();
