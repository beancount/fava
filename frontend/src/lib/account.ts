/**
 * Obtain the parent account name.
 * @param name - an account name.
 */
export function parent(name: string): string {
  const parentEnd = name.lastIndexOf(":");
  return parentEnd > 0 ? name.slice(0, parentEnd) : "";
}

/**
 * Obtain the leaf part of the account name, the last segment.
 * @param name - an account name.
 */
export function leaf(name: string): string {
  const parentEnd = name.lastIndexOf(":");
  return parentEnd > 0 ? name.slice(parentEnd + 1) : name;
}

/**
 * Check whether an account is a descendant of another.
 * @param name - an account name.
 * @param of - the possible ancestor
 */
export function isDescendant(name: string, of: string): boolean {
  if (of === "") {
    return true;
  }
  return name === of || name.startsWith(`${of}:`);
}
