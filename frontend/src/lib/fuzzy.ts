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

export type FuzzyWrappedText = ["text" | "match", string][];

/**
 * Wrap fuzzy matched characters.
 *
 * Wrap all occurences of characters of `pattern` (in order) in `string` in
 * tuples with a "match" marker (and the others as plain "text") to allow for
 * the matches to be wrapped in markers to highlight them in the HTML.
 */
export function fuzzywrap(pattern: string, text: string): FuzzyWrappedText {
  if (!pattern) {
    return [["text", text]];
  }
  const casesensitive = pattern === pattern.toLowerCase();
  const exact = casesensitive
    ? text.toLowerCase().indexOf(pattern)
    : text.indexOf(pattern);
  if (exact > -1) {
    const before = text.slice(0, exact);
    const match = text.slice(exact, exact + pattern.length);
    const after = text.slice(exact + pattern.length);
    const result: FuzzyWrappedText = [];
    if (before) {
      result.push(["text", before]);
    }
    result.push(["match", match]);
    if (after) {
      result.push(["text", after]);
    }
    return result;
  }
  // current index into the pattern
  let pindex = 0;
  // current unmatched string
  let plain: string | null = null;
  // current matched string
  let match: string | null = null;
  const result: FuzzyWrappedText = [];
  for (const char of text) {
    const search = pattern[pindex];
    if (char === search || char.toLowerCase() === search) {
      match = match != null ? match + char : char;
      if (plain != null) {
        result.push(["text", plain]);
        plain = null;
      }
      pindex += 1;
    } else {
      plain = plain != null ? plain + char : char;
      if (match != null) {
        result.push(["match", match]);
        match = null;
      }
    }
  }
  if (pindex < pattern.length) {
    return [["text", text]];
  }
  if (plain != null) {
    result.push(["text", plain]);
    plain = null;
  }
  if (match != null) {
    result.push(["match", match]);
    match = null;
  }
  return result;
}
