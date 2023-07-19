/**
 * Fava extensions might contain their own Javascript code, this module
 * contains the functionality to handle them.
 */

import { get as store_get } from "svelte/store";

import { getUrlPath, urlFor } from "./helpers";
import { log_error } from "./log";
import { extensions } from "./stores";

/**
 * The Javascript code of a Fava extension should export an object of this type.
 */
export interface ExtensionModule {
  /** Initialise this Javascript module / run some code on the initial load. */
  init?: () => void;
  /** Run some code after any Fava page has loaded. */
  onPageLoad?: () => void;
  /** Run some code after the page for this extension has loaded. */
  onExtensionPageLoad?: () => void;
}

async function loadExtensionModule(name: string): Promise<ExtensionModule> {
  const url = urlFor(`extension_js_module/${name}.js`, undefined, false);
  const mod = await (import(url) as Promise<{ default?: ExtensionModule }>);
  if (typeof mod.default === "object") {
    return mod.default;
  }
  throw new Error(
    `Error importing module for extension ${name}: module must export "default" object`,
  );
}

/** A map of all extensions modules that have been (requested to be) loaded already. */
const loaded_extensions = new Map<string, Promise<ExtensionModule>>();

/** Get the extensions module - if it has not been imported yet, initialise it. */
async function getExt(name: string): Promise<ExtensionModule> {
  const loaded_ext = loaded_extensions.get(name);
  if (loaded_ext) {
    return loaded_ext;
  }
  const ext = loadExtensionModule(name);
  loaded_extensions.set(name, ext);
  (await ext).init?.();
  return ext;
}

/**
 * On page load, run check if the new page is an extension report page and run hooks.
 */
export function handleExtensionPageLoad(): void {
  const exts = store_get(extensions).filter((e) => e.has_js_module);
  for (const { name } of exts) {
    // Run the onPageLoad handler for all pages.
    getExt(name)
      .then((m) => m.onPageLoad?.())
      .catch(log_error);
  }
  const path = getUrlPath(window.location);
  if (path?.startsWith("extension/")) {
    for (const { name } of exts) {
      if (path.startsWith(`extension/${name}`)) {
        getExt(name)
          .then((m) => m.onExtensionPageLoad?.())
          .catch(log_error);
      }
    }
  }
}
