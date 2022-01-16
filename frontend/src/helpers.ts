import { get } from "svelte/store";

import type { Entry } from "./entries";
import { baseURL } from "./stores";
import { urlSyncedParams } from "./stores/url";

/**
 * Get the URL string for one of Fava's reports.
 */
export function urlFor(
  report: string,
  params?: Record<string, string | number | undefined>,
  update = true
): string {
  const url = `${get(baseURL)}${report}`;
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
export function urlForSource(entry: Entry): string {
  const file_path = entry.meta.filename.toString();
  const line = entry.meta.lineno.toString();
  return urlFor("editor/", { file_path, line });
}

/** URL for the account report. */
export function urlForAccount(account: string): string {
  return urlFor(`account/${account}/`);
}
