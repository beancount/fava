/** A type for an array with at least one element. */
export type NonEmptyArray<T> = [T, ...T[]];

/** Type guard for non-empty array. */
export function is_non_empty<T>(array: T[]): array is NonEmptyArray<T> {
  return array.length > 0;
}
