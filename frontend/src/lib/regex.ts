/**
 * Escape the value to produce a valid regex for the Fava filter.
 */
export function escape_for_regex(value: string): string {
  return value.replace(/[.*+\-?^${}()|[\]\\]/g, "\\$&");
}
