/** Types for which we can do a strict comparison. */
export type StrictEquality = string | number | null;

/**
 * Shallow equality of two arrays - the elements are compared strictly.
 */
export function shallow_equal<T extends StrictEquality>(
  a: readonly T[],
  b: readonly T[],
): boolean {
  const l = a.length;
  if (l !== b.length) {
    return false;
  }

  for (let i = 0; i < l; i += 1) {
    if (a[i] !== b[i]) {
      return false;
    }
  }

  return true;
}
