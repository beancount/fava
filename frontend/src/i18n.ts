import { record, string } from "./lib/validation";
import { getScriptTagJSON } from "./lib/dom";

let translations: Record<string, string>;

/**
 * Translate the given string.
 */
export function _(text: string): string {
  if (translations === undefined) {
    translations = record(string)(getScriptTagJSON("#translations"));
  }
  return translations[text] || text;
}
