import { get } from "svelte/store";

import { base_url, fava_options } from "./stores";
import { urlSyncedParams } from "./stores/url";

/**
 * Get the URL string for one of Fava's reports.
 */
export function urlFor(
  report: string,
  params?: Record<string, string | number | undefined>,
  update = true
): string {
  const url = `${get(base_url)}${report}`;
  const urlParams = new URLSearchParams();
  if (update) {
    const oldParams = new URL(window.location.href).searchParams;
    for (const name of urlSyncedParams) {
      const value = oldParams.get(name);
      if (value) {
        urlParams.set(name, value);
      }
    }
  }
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        urlParams.set(key, `${value}`);
      }
    });
  }
  const urlParamString = urlParams.toString();
  return urlParamString ? `${url}?${urlParams.toString()}` : url;
}

/** URL for the editor to the source location of an entry. */
export function urlForSource(file_path: string, line: string): string {
  return get(fava_options).use_external_editor
    ? `beancount://${file_path}?lineno=${line}`
    : urlFor("editor/", { file_path, line });
}

/** URL for the account report. */
export function urlForAccount(account: string): string {
  return urlFor(`account/${account}/`);
}
