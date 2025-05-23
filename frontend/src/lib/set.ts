/**
 * Toggle an element in a set (mutating and returning it).
 */
export function toggle<T>(set: Set<T>, element: T): Set<T> {
  if (set.has(element)) {
    set.delete(element);
  } else {
    set.add(element);
  }
  return set;
}
