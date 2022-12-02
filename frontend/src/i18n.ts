import { getScriptTagValue } from "./lib/dom";
import { record, string } from "./lib/validation";
import { log_error } from "./log";

let translations: Record<string, string> | undefined;
const validator = record(string);

/**
 * Translate the given string.
 */
export function _(text: string): string {
  if (translations === undefined) {
    const res = getScriptTagValue("#translations", validator);
    translations = res.success ? res.value : {};
    if (!res.success) {
      log_error(`Loading translations failed: ${res.value}`);
    }
  }
  return translations[text] ?? text;
}

/**
 * Replace the placeholders in a translation string.
 */
export function format(text: string, values: Record<string, string>): string {
  return text.replace(
    /%\(\w+\)s/g,
    (match) => values[match.slice(2, -2)] ?? "MISSING"
  );
}
