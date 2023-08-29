/**
 * Fuzzy match a pattern against a string.
 *
 * @param pattern The pattern to search for.
 * @param text The string to search in.
 *
 * Returns a score greater than zero if all characters of `pattern` can be
 * found in order in `string`. For lowercase characters in `pattern` match both
 * lower and upper case, for uppercase only an exact match counts.
 */
export function fuzzytest(pattern: string, text: string): number {
  const casesensitive = pattern === pattern.toLowerCase();
  const exact = casesensitive
    ? text.toLowerCase().indexOf(pattern)
    : text.indexOf(pattern);
  if (exact > -1) {
    return pattern.length ** 2;
  }
  let score = 0;
  let localScore = 0;
  let pindex = 0;
  for (const char of text) {
    const search = pattern[pindex];
    if (char === search || char.toLowerCase() === search) {
      pindex += 1;
      localScore += +1;
    } else {
      localScore = 0;
    }
    score += localScore;
  }
  return pindex === pattern.length ? score : 0;
}

/**
 * Filter a list of possible suggestions to only those that match the pattern
 */
export function fuzzyfilter(
  pattern: string,
  suggestions: readonly string[],
): readonly string[] {
  if (!pattern) {
    return suggestions;
  }
  return suggestions
    .map((s): [string, number] => [s, fuzzytest(pattern, s)])
    .filter(([, score]) => score)
    .sort((a, b) => b[1] - a[1])
    .map(([s]) => s);
}
const escapeChars: Record<string, string> = {
  '"': "&quot;",
  "'": "&#39;",
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
};
const e = (text: string) =>
  text.replace(/["'&<>]/g, (m) => escapeChars[m] ?? m);

/**
 * Wrap fuzzy matched characters.
 *
 * Wrap all occurences of characters of `pattern` (in order) in `string` in
 * <span> tags.
 */
export function fuzzywrap(pattern: string, text: string): string {
  if (!pattern) {
    return e(text);
  }
  const casesensitive = pattern === pattern.toLowerCase();
  const exact = casesensitive
    ? text.toLowerCase().indexOf(pattern)
    : text.indexOf(pattern);
  if (exact > -1) {
    const before = text.slice(0, exact);
    const match = text.slice(exact, exact + pattern.length);
    const after = text.slice(exact + pattern.length);
    return `${e(before)}<span>${e(match)}</span>${e(after)}`;
  }
  let pindex = 0;
  let inMatch = false;
  const result = [];
  for (const char of text) {
    const search = pattern[pindex];
    if (char === search || char.toLowerCase() === search) {
      if (!inMatch) {
        result.push("<span>");
        inMatch = true;
      }
      result.push(e(char));
      pindex += 1;
    } else {
      if (inMatch) {
        result.push("</span>");
        inMatch = false;
      }
      result.push(e(char));
    }
  }
  if (pindex < pattern.length) {
    return e(text);
  }
  if (inMatch) {
    result.push("</span>");
  }
  return result.join("");
}
