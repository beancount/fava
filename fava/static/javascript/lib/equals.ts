/**
 * Shallow equality of two arrays.
 */
export function shallow_equal<T>(a: T[], b: T[]): boolean {
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
