import { derived, get as store_get } from "svelte/store";

import { base_url, fava_options } from "./stores";
import { searchParams, urlSyncedParams } from "./stores/url";

/**
 * Get the URL path relative to the base url of the current ledger.
 */
export function getUrlPath(
  url: Pick<URL | Location, "pathname">,
): string | null {
  const $base_url = store_get(base_url);
  return $base_url && url.pathname.startsWith($base_url)
    ? decodeURI(url.pathname.slice($base_url.length))
    : null;
}

/**
 * Get the URL string for one of Fava's reports (pure internal function, just exported for tests).
 * @param $base_url - the current value of base_url
 * @param $searchParams - the current value of searchParams or null
 *                        if url-synced parameters are not needed.
 * @param report - report name
 * @param params - URL params to set
 * @returns The URL string.
 */
export function urlForInternal(
  $base_url: string,
  $searchParams: URLSearchParams | null,
  report: string,
  params: Record<string, string | number | undefined> | undefined,
): string {
  const url = `${$base_url}${report}`;
  const urlParams = new URLSearchParams();
  if ($searchParams) {
    for (const name of urlSyncedParams) {
      const value = $searchParams.get(name);
      if (value != null) {
        urlParams.set(name, value);
      }
    }
  }
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        urlParams.set(key, value.toString());
      }
    });
  }
  const urlParamString = urlParams.toString();
  return urlParamString ? `${url}?${urlParams.toString()}` : url;
}

/**
 * Get the URL string for one of Fava's reports.
 */
export function urlFor(
  report: string,
  params?: Record<string, string | number | undefined>,
  update = true,
): string {
  const $base_url = store_get(base_url);
  const $searchParams = update ? store_get(searchParams) : null;
  return urlForInternal($base_url, $searchParams, report, params);
}

/** URL for the editor to the source location of an entry. */
export function urlForSource(file_path: string, line: string): string {
  return store_get(fava_options).use_external_editor
    ? `beancount://${file_path}?lineno=${line}`
    : urlFor("editor/", { file_path, line });
}

/** URL for the account report (derived store to keep track of filter changes.). */
export const urlForAccount = derived(
  [base_url, searchParams],
  ([$base_url, $searchParams]) =>
    (account: string, params?: Record<string, string>): string =>
      urlForInternal($base_url, $searchParams, `account/${account}/`, params),
);
