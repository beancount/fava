import { baseURL, urlSyncedParams } from "./stores/url";

let baseURL_val = "";
baseURL.subscribe((val) => {
  baseURL_val = val;
});

/**
 * Get the URL string for one of Fava's reports.
 */
export function urlFor(
  report: string,
  params?: Record<string, string>,
  update = true
): string {
  const url = `${baseURL_val}${report}`;
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
      urlParams.set(key, value);
    });
  }
  const urlParamString = urlParams.toString();
  return urlParamString ? `${url}?${urlParams.toString()}` : url;
}

/** Url for the account page for an account. */
export function accountUrl(account: string): string {
  return new URL(urlFor(`account/${account}`), window.location.href).toString();
}
