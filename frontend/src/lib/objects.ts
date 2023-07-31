/** Whether the given object is empty. */
export function is_empty(obj: Record<string, unknown>): boolean {
  return Object.keys(obj).length === 0;
}
