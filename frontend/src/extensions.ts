/**
 * Fava extensions might contain their own Javascript code, this module
 * contains the functionality to handle them.
 */

import { get as store_get } from "svelte/store";

import type {
  ExtensionApi,
  ExtensionContext,
  ExtensionModule,
} from "./extension-api.d.ts";
import { getUrlPath, urlForRaw } from "./helpers.ts";
import { log_error } from "./log.ts";
import { extensions } from "./stores/index.ts";

/** Helpers to make requests. */
class ExtensionApiImpl implements ExtensionApi {
  /** The extension name. */
  #name: string;

  constructor(name: string) {
    this.#name = name;
  }

  async request(
    endpoint: string,
    method: "GET" | "PUT" | "POST" | "DELETE",
    params?: Record<string, string | number>,
    body?: unknown,
    output: "json" | "string" | "raw" = "json",
  ): Promise<unknown> {
    const $urlForRaw = store_get(urlForRaw);
    const url = $urlForRaw(`extension/${this.#name}/${endpoint}`, params);
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
  async get(
    endpoint: string,
    params: Record<string, string>,
  ): Promise<unknown> {
    return this.request(endpoint, "GET", params, undefined);
  }
  async put(endpoint: string, body?: unknown): Promise<unknown> {
    return this.request(endpoint, "PUT", undefined, body);
  }
  async post(endpoint: string, body?: unknown): Promise<unknown> {
    return this.request(endpoint, "POST", undefined, body);
  }
  async delete(endpoint: string): Promise<unknown> {
    return this.request(endpoint, "DELETE");
  }
}

class ExtensionData {
  readonly #extension: ExtensionModule;
  readonly #context: ExtensionContext;

  constructor(extension: ExtensionModule, context: ExtensionContext) {
    this.#extension = extension;
    this.#context = context;
  }

  async init(): Promise<void> {
    await this.#extension.init?.(this.#context);
  }

  onPageLoad(): void {
    this.#extension.onPageLoad?.(this.#context);
  }

  onExtensionPageLoad(): void {
    this.#extension.onExtensionPageLoad?.(this.#context);
  }
}

async function load_extension_module(name: string): Promise<ExtensionData> {
  const $urlForRaw = store_get(urlForRaw);
  const url = $urlForRaw(`extension_js_module/${name}.js`);
  const mod = await (import(url) as Promise<{ default?: ExtensionModule }>);
  if (typeof mod.default === "object") {
    return new ExtensionData(mod.default, { api: new ExtensionApiImpl(name) });
  }
  throw new Error(
    `Error importing module for extension ${name}: module must export "default" object`,
  );
}

/** A map of all extensions modules that have been (requested to be) loaded already. */
const loaded_extensions = new Map<string, Promise<ExtensionData>>();

/** Get the extensions module - if it has not been imported yet, initialise it. */
async function get_or_init_extension(name: string): Promise<ExtensionData> {
  const loaded_ext = loaded_extensions.get(name);
  if (loaded_ext) {
    return loaded_ext;
  }
  const ext_promise = load_extension_module(name);
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
    get_or_init_extension(name)
      .then((m) => {
        m.onPageLoad();
      })
      .catch(log_error);
  }
  const path = getUrlPath(window.location).unwrap_or("");
  if (path.startsWith("extension/")) {
    for (const { name } of exts) {
      if (path.startsWith(`extension/${name}`)) {
        get_or_init_extension(name)
          .then((m) => {
            m.onExtensionPageLoad();
          })
          .catch(log_error);
      }
    }
  }
}
