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

/** The context that an extensions handlers are called with. */
export interface ExtensionContext {
  /** Helpers to make requests. */
  api: ExtensionApi;
}

/** Helpers to make requests. */
interface ExtensionApi {
  /** Send a request to an extension endpoint. */
  request(
    endpoint: string,
    method: "GET" | "PUT" | "POST" | "DELETE",
    params?: Record<string, string | number>,
    body?: unknown,
    output?: "json" | "string" | "raw",
  ): Promise<unknown>;

  /** GET an endpoint with parameters and return JSON. */
  get(endpoint: string, params: Record<string, string>): Promise<unknown>;

  /** PUT an endpoint with a body and return JSON. */
  put(endpoint: string, body?: unknown): Promise<unknown>;

  /** POST to an endpoint with a body and return JSON. */
  post(endpoint: string, body?: unknown): Promise<unknown>;

  /** DELETE an endpoint and return JSON. */
  delete(endpoint: string): Promise<unknown>;
}
