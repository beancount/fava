import { parseJSON } from "./json";
import type { Result } from "./result";
import { err } from "./result";
import type { ValidationError, Validator } from "./validation";

class ScriptTagNotFoundError extends Error {
  constructor(selector: string) {
    super(`<script> tag not found for selector '${selector}'`);
  }
}

/**
 * Get the parsed content of a script tag containing JSON.
 * @param selector A DOM selector string.
 */
function getScriptTagJSON(
  selector: string,
): Result<unknown, ScriptTagNotFoundError | SyntaxError> {
  const el = document.querySelector(selector);
  if (!el) {
    return err(new ScriptTagNotFoundError(selector));
  }
  return parseJSON(el.textContent ?? "");
}

/**
 * Get the parsed content of a script tag containing JSON.
 * @param selector - A DOM selector string.
 * @param validator - Validator for the contents of the <script> tag.
 */
export function getScriptTagValue<T>(
  selector: string,
  validator: Validator<T>,
): Result<T, ScriptTagNotFoundError | SyntaxError | ValidationError> {
  return getScriptTagJSON(selector).and_then(validator);
}
