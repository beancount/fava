/** A type for an array with at least one element. */
export type NonEmptyArray<T> = readonly [T, ...T[]];

/** Type guard for non-empty array. */
export function is_non_empty<T>(
  array: readonly T[],
): array is NonEmptyArray<T> {
  return array.length > 0;
}

/** Get the last element of an non-empty array. */
export function last_element<T>(array: NonEmptyArray<T>): T {
  return array[array.length - 1] as T;
}

/**
 * Move an element from one position to another and return a copy.
 *
 * @param array - The array to operate on.
 * @param from - The array index of the element to move.
 * @param to - The array index to move it to.
 */
export function move<T>(
  array: readonly T[],
  from: number,
  to: number,
): readonly T[] {
  const moved = array[from];
  if (moved != null) {
    const updated = array.toSpliced(from, 1);
    updated.splice(to, 0, moved);
    return updated;
  }
  return array;
}
