import { getScriptTagJSON } from "./lib/dom";
import { record, string } from "./lib/validation";

let translations: Record<string, string>;

/**
 * Translate the given string.
 */
export function _(text: string): string {
  if (translations === undefined) {
    const res = record(string)(getScriptTagJSON("#translations"));
    translations = res.success ? res.value : {};
    // TODO log error.
  }
  return translations[text] || text;
}
