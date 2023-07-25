import { parseJSON } from "./json";
import type { Result } from "./result";
import { err } from "./result";
import type { Validator } from "./validation";

/**
 * Get the parsed content of a script tag containing JSON.
 * @param selector A DOM selector string.
 */
function getScriptTagJSON(selector: string): Result<unknown, string> {
  const el = document.querySelector(selector);
  if (!el) {
    return err(`<script> tag not found for selector '${selector}'`);
  }
  try {
    return parseJSON(el.textContent ?? "");
  } catch (e) {
    return err(`<script> tag for selector '${selector}' contains invalid JSON`);
  }
}

/**
 * Get the parsed content of a script tag containing JSON.
 * @param selector - A DOM selector string.
 * @param validator - Validator for the contents of the <script> tag.
 */
export function getScriptTagValue<T>(
  selector: string,
  validator: Validator<T>,
): Result<T, string> {
  return getScriptTagJSON(selector).and_then(validator);
}
