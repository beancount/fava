import { getScriptTagValue } from "./lib/dom";
import { ok } from "./lib/result";
import { record, string } from "./lib/validation";
import { log_error } from "./log";

let translations: Record<string, string> | undefined;
const validator = record(string);

/**
 * Translate the given string.
 */
// eslint-disable-next-line @typescript-eslint/naming-convention
export function _(text: string): string {
  if (translations === undefined) {
    const res =
      // The DOM is not available in tests
      // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
      globalThis.document !== undefined
        ? getScriptTagValue("#translations", validator)
        : ok({});
    translations = res.unwrap_or({});
    if (res.is_err) {
      log_error(`Loading translations failed:`, res.error);
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
    (match) => values[match.slice(2, -2)] ?? "MISSING",
  );
}
