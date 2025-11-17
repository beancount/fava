import { parseJSON } from "./json.ts";
import type { Result } from "./result.ts";
import { err } from "./result.ts";
import type { ValidationError, Validator } from "./validation.ts";

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
  return parseJSON(el.textContent);
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

/**
 * Create a document fragment from a string of HTML.
 */
export function fragment_from_string(html: string): DocumentFragment {
  const template = document.createElement("template");
  template.innerHTML = html;
  return template.content;
}

/**
 * Get the containing element for an `EventTarget`.
 */
export function get_el(target: EventTarget | null): Element | null {
  if (target instanceof Node) {
    return target instanceof Element ? target : target.parentElement;
  }
  return null;
}
