/**
 * Get the parsed content of a script tag containing JSON.
 * @param selector A DOM selector string.
 */
export function getScriptTagJSON(selector: string): unknown {
  const el = document.querySelector(selector);
  return el ? JSON.parse(el.innerHTML) : null;
}
