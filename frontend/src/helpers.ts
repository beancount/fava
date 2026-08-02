import { derived, get as store_get } from "svelte/store";

import type { Result } from "./lib/result.ts";
import { err, ok } from "./lib/result.ts";
import { use_external_editor } from "./stores/fava_options.ts";
import { base_url } from "./stores/index.ts";
import { synced_search_params } from "./stores/url.ts";

export class NonRelativeUrlPathError extends Error {
  constructor(pathname: string, $base_url: string) {
    super(`Path '${pathname}' not relative to base url '${$base_url}'.`);
  }
}

/**
 * Get the URL path relative to the base url of the current ledger.
 */
export function get_url_path(
  url: Pick<URL | Location, "pathname">,
): Result<string, NonRelativeUrlPathError> {
  const { pathname } = url;
  const $base_url = store_get(base_url);
  return $base_url && pathname.startsWith($base_url)
    ? ok(decodeURI(pathname.slice($base_url.length)))
    : err(new NonRelativeUrlPathError(pathname, $base_url));
}

/**
 * Get the URL string for one of Fava's reports (pure internal function, just exported for tests).
 * @param $base_url - the current value of base_url
 * @param $search_params - the current value of search_params or null
 *                        if url-synced parameters are not needed.
 * @param report - report name
 * @param params - URL params to set
 * @returns The URL string.
 */
export function url_for_internal(
  $base_url: string,
  $synced_search_params: URLSearchParams | null,
  report: string,
  params: Record<string, string | number | undefined> | undefined,
): string {
  const url = `${$base_url}${report}`;
  const url_params = $synced_search_params
    ? new URLSearchParams($synced_search_params)
    : new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value != null) {
        url_params.set(key, value.toString());
      }
    });
  }
  const url_param_string = url_params.toString();
  return url_param_string ? `${url}?${url_params.toString()}` : url;
}

/**
 * Get the URL string for one of Fava's reports.
 */
export const url_for = derived(
  [base_url, synced_search_params],
  ([$base_url, $synced_search_params]) =>
    (
      report:
        | `${string}/`
        | `download-journal`
        | `download-query/query_result.${string}`
        | `help/${string}`,
      params?: Record<string, string | number | undefined>,
    ): string =>
      url_for_internal($base_url, $synced_search_params, report, params),
);

/**
 * Get the URL string for one of Fava's reports - without synced params.
 */
export const url_for_raw = derived(
  [base_url],
  ([$base_url]) =>
    (
      report: string,
      params?: Record<string, string | number | undefined>,
    ): string =>
      url_for_internal($base_url, null, report, params),
);

/** URL for the editor to the source location of an entry. */
export const url_for_source = derived(
  [url_for, use_external_editor],
  ([$url_for, $use_external_editor]) =>
    (file_path: string, line: string): string =>
      $use_external_editor
        ? `beancount://${file_path}?lineno=${line}`
        : $url_for("editor/", { file_path, line }),
);

/** URL for the account report (derived store to keep track of filter changes.). */
export const url_for_account = derived(
  url_for,
  ($url_for) =>
    (account: string, params?: Record<string, string>): string =>
      $url_for(`account/${account}/`, params),
);
