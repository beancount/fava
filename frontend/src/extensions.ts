/**
 * Fava extensions might contain their own Javascript code, this module
 * contains the functionality to handle them.
 */

import { get as store_get } from "svelte/store";

import { getUrlPath, urlForRaw } from "./helpers";
import { fetch } from "./lib/fetch";
import { log_error } from "./log";
import { extensions } from "./stores";

/** Helpers to make requests. */
export class ExtensionApi {
  constructor(private readonly name: string) {}

  /** Send a request to an extension endpoint. */
  async request(
    endpoint: string,
    method: "GET" | "PUT" | "POST" | "DELETE",
    params?: Record<string, string | number>,
    body?: unknown,
    output: "json" | "string" | "raw" = "json",
  ): Promise<unknown> {
    const $urlForRaw = store_get(urlForRaw);
    const url = $urlForRaw(`extension/${this.name}/${endpoint}`, params);
    let opts = {};
    if (body != null) {
      opts =
        body instanceof FormData
          ? { body }
          : {
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(body),
            };
    }
    const response = await fetch(url, { method, ...opts });
    if (output === "json") {
      return response.json();
    }
    if (output === "string") {
      return response.text();
    }
    return response;
  }

  /** GET an endpoint with parameters and return JSON. */
  async get(
    endpoint: string,
    params: Record<string, string>,
  ): Promise<unknown> {
    return this.request(endpoint, "GET", params, undefined);
  }

  /** GET an endpoint with a body and return JSON. */
  async put(endpoint: string, body?: unknown): Promise<unknown> {
    return this.request(endpoint, "PUT", undefined, body);
  }

  /** POST to an endpoint with a body and return JSON. */
  async post(endpoint: string, body?: unknown): Promise<unknown> {
    return this.request(endpoint, "POST", undefined, body);
  }

  /** DELETE an endpoint and return JSON. */
  async delete(endpoint: string): Promise<unknown> {
    return this.request(endpoint, "DELETE");
  }
}

/** The context that an extensions handlers are called with. */
export interface ExtensionContext {
  /** Helpers to make requests. */
  api: ExtensionApi;
}

/**
 * The Javascript code of a Fava extension should export an object of this type.
 *
 * The extension will be initialised when Fava loads by a call to init(). It can also
 * provider handlers that are run on each subsequent page load (either all or just
 * pages of the extension itself).
 */
export interface ExtensionModule {
  /** Initialise this Javascript module / run some code on the initial load. */
  init?: (c: ExtensionContext) => void | Promise<void>;
  /** Run some code after any Fava page has loaded. */
  onPageLoad?: (c: ExtensionContext) => void;
  /** Run some code after a page for this extension has loaded. */
  onExtensionPageLoad?: (c: ExtensionContext) => void;
}

class ExtensionData {
  constructor(
    private readonly extension: ExtensionModule,
    private readonly context: ExtensionContext,
  ) {}

  async init(): Promise<void> {
    await this.extension.init?.(this.context);
  }

  onPageLoad(): void {
    this.extension.onPageLoad?.(this.context);
  }

  onExtensionPageLoad(): void {
    this.extension.onExtensionPageLoad?.(this.context);
  }
}

async function loadExtensionModule(name: string): Promise<ExtensionData> {
  const $urlForRaw = store_get(urlForRaw);
  const url = $urlForRaw(`extension_js_module/${name}.js`);
  const mod = await (import(url) as Promise<{ default?: ExtensionModule }>);
  if (typeof mod.default === "object") {
    return new ExtensionData(mod.default, { api: new ExtensionApi(name) });
  }
  throw new Error(
    `Error importing module for extension ${name}: module must export "default" object`,
  );
}

/** A map of all extensions modules that have been (requested to be) loaded already. */
const loaded_extensions = new Map<string, Promise<ExtensionData>>();

/** Get the extensions module - if it has not been imported yet, initialise it. */
async function getOrInitExtension(name: string): Promise<ExtensionData> {
  const loaded_ext = loaded_extensions.get(name);
  if (loaded_ext) {
    return loaded_ext;
  }
  const ext_promise = loadExtensionModule(name);
  loaded_extensions.set(name, ext_promise);
  await (await ext_promise).init();
  return ext_promise;
}

/**
 * On page load, run check if the new page is an extension report page and run hooks.
 */
export function handleExtensionPageLoad(): void {
  const exts = store_get(extensions).filter((e) => e.has_js_module);
  for (const { name } of exts) {
    // Run the onPageLoad handler for all pages.
    getOrInitExtension(name)
      .then((m) => {
        m.onPageLoad();
      })
      .catch(log_error);
  }
  const path = getUrlPath(window.location) ?? "";
  if (path.startsWith("extension/")) {
    for (const { name } of exts) {
      if (path.startsWith(`extension/${name}`)) {
        getOrInitExtension(name)
          .then((m) => {
            m.onExtensionPageLoad();
          })
          .catch(log_error);
      }
    }
  }
}
