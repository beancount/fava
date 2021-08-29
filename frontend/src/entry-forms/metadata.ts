/**
 * Convert a metadata value to a string ready for an input field.
 * @param value - the metadata value.
 */
export function metaValueToString(value: string | boolean): string {
  if (typeof value === "boolean") {
    return value ? "TRUE" : "FALSE";
  }
  return value;
}

/**
 * Convert a string to a metadata value.
 * @param s - The string that the user entered.
 */
export function stringToMetaValue(s: string): string | boolean {
  if (s === "TRUE") {
    return true;
  }
  if (s === "FALSE") {
    return false;
  }
  return s;
}
