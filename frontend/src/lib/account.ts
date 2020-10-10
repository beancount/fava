/**
 * Obtain the parent account name.
 * @param name - an account name.
 */
export function parent(name: string): string {
  const parentEnd = name.lastIndexOf(":");
  return parentEnd > 0 ? name.slice(0, parentEnd) : "";
}

/**
 * Obtain the leaf part of the account name.
 * @param name - an account name.
 */
export function leaf(name: string): string {
  const parentEnd = name.lastIndexOf(":");
  return parentEnd > 0 ? name.slice(parentEnd + 1) : name;
}
