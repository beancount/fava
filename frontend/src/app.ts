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

import { get_changed, get_errors, get_ledger_data } from "./api/index.ts";
import { ledgerDataValidator } from "./api/validators.ts";
import { CopyableText } from "./clipboard.ts";
import { BeancountTextarea } from "./codemirror/dom.ts";
import { _ } from "./i18n.ts";
import { init_global_keyboard_shortcuts } from "./keyboard-shortcuts.ts";
import { get_script_tag_value } from "./lib/dom.ts";
import { log_error } from "./log.ts";
import { notify, notify_err } from "./notifications.ts";
import { frontend_routes } from "./reports/routes.ts";
import { router } from "./router.ts";
import { init_sidebar } from "./sidebar/index.ts";
import { has_changes } from "./sidebar/page-title.ts";
import { SortableTable } from "./sort/sortable-table.ts";
import { init_color_scheme } from "./stores/color_scheme.ts";
import {
  auto_reload,
  invert_gains_losses_colors,
} from "./stores/fava_options.ts";
import { errors, ledgerData } from "./stores/index.ts";
import { ledger_mtime, read_mtime } from "./stores/mtime.ts";
import { SvelteCustomElement } from "./svelte-custom-elements.ts";
import { TreeTableCustomElement } from "./tree-table/tree-table-custom-element.ts";

/**
 * Define the custom elements that Fava uses.
 */
function define_custom_elements() {
  customElements.define("beancount-textarea", BeancountTextarea, {
    extends: "textarea",
  });
  customElements.define("copyable-text", CopyableText);
  customElements.define("svelte-component", SvelteCustomElement);

  // for extension compatibility (only used in _query_table.html)
  customElements.define("sortable-table", SortableTable, { extends: "table" });
  // for extension compatibility
  customElements.define("tree-table", TreeTableCustomElement);
}

/**
 * Update the ledger data and errors; Reload if automatic reloading is configured.
 */
function on_changes() {
  get_ledger_data()
    .then((v) => {
      ledgerData.set(v);
    })
    .catch((e: unknown) => {
      notify_err(e, (err) => `Error fetching ledger data: ${err.message}`);
    });
  if (store_get(auto_reload) && !router.has_interrupt_handler) {
    router.reload();
  } else {
    get_errors().then((v) => {
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
function poll_for_changes(): void {
  get_changed().catch(log_error);
}

function init(): void {
  const initial = get_script_tag_value("#ledger-data", ledgerDataValidator);
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
    on_changes();
  });

  router.init(frontend_routes);
  init_sidebar();
  init_global_keyboard_shortcuts();
  define_custom_elements();
  setInterval(poll_for_changes, 5000);

  ledgerData.subscribe((val) => {
    errors.set(val.errors);
  });

  init_color_scheme();

  invert_gains_losses_colors.subscribe(($invert) => {
    document.documentElement.classList.toggle("invert-gains-losses", $invert);
  });
}

init();
