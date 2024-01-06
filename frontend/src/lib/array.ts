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
