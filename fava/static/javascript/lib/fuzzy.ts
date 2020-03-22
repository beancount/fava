/**
 * Fuzzy match a pattern against a string.
 *
 * @param pattern The pattern to search for.
 * @param text The string to search in.
 *
 * Returns true if all characters of `pattern` can be found in order in
 * `string`. For lowercase characters in `pattern` match both lower and upper
 * case, for uppercase only an exact match counts.
 */
export function fuzzytest(pattern: string, text: string): boolean {
  let pindex = 0;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const search = pattern[pindex];
    if (char === search || char.toLowerCase() === search) {
      pindex += 1;
    }
  }
  return pindex === pattern.length;
}

/**
 * Wrap fuzzy matched characters.
 *
 * Wrap all occurences of characters of `pattern` (in order) in `string` in
 * <span> tags.
 */
export function fuzzywrap(pattern: string, text: string): string {
  let pindex = 0;
  let inMatch = false;
  const result = [];
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const search = pattern[pindex];
    if (char === search || char.toLowerCase() === search) {
      if (!inMatch) {
        result.push("<span>");
        inMatch = true;
      }
      result.push(char);
      pindex += 1;
    } else {
      if (inMatch) {
        result.push("</span>");
        inMatch = false;
      }
      result.push(char);
    }
  }
  if (inMatch) {
    result.push("</span>");
  }
  return result.join("");
}
