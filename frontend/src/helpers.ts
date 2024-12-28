import { derived, get as store_get } from "svelte/store";

import { base_url, fava_options } from "./stores";
import { syncedSearchParams } from "./stores/url";

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
  $syncedSearchParams: URLSearchParams | null,
  report: string,
  params: Record<string, string | number | undefined> | undefined,
): string {
  const url = `${$base_url}${report}`;
  const urlParams = $syncedSearchParams
    ? new URLSearchParams($syncedSearchParams)
    : new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value != null) {
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
export const urlFor = derived(
  [base_url, syncedSearchParams],
  ([$base_url, $syncedSearchParams]) =>
    (
      report: string,
      params?: Record<string, string | number | undefined>,
    ): string =>
      urlForInternal($base_url, $syncedSearchParams, report, params),
);

/**
 * Get the URL string for one of Fava's reports - without synced params.
 */
export const urlForRaw = derived(
  [base_url],
  ([$base_url]) =>
    (
      report: string,
      params?: Record<string, string | number | undefined>,
    ): string =>
      urlForInternal($base_url, null, report, params),
);

const use_external_editor = derived(
  fava_options,
  ($fava_options) => $fava_options.use_external_editor,
);

/** URL for the editor to the source location of an entry. */
export const urlForSource = derived(
  [urlFor, use_external_editor],
  ([$urlFor, $use_external_editor]) =>
    (file_path: string, line: string): string =>
      $use_external_editor
        ? `beancount://${file_path}?lineno=${line}`
        : $urlFor("editor/", { file_path, line }),
);

/** URL for the account report (derived store to keep track of filter changes.). */
export const urlForAccount = derived(
  urlFor,
  ($urlFor) =>
    (account: string, params?: Record<string, string>): string =>
      $urlFor(`account/${account}/`, params),
);
