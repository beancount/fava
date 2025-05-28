import { sort } from "d3-array";

/**
 * Obtain the parent account name.
 * @param name - an account name.
 */
export function parent(name: string): string {
  const parent_end = name.lastIndexOf(":");
  return parent_end > 0 ? name.slice(0, parent_end) : "";
}

/**
 * Obtain the leaf part of the account name, the last segment.
 * @param name - an account name.
 */
export function leaf(name: string): string {
  const parent_end = name.lastIndexOf(":");
  return parent_end > 0 ? name.slice(parent_end + 1) : name;
}

/**
 * Get the ancestors of an account (including itself).
 * @param name - an account name.
 */
export function ancestors(name: string): string[] {
  const result: string[] = [];
  let index = name.indexOf(":");
  while (index !== -1) {
    result.push(name.slice(0, index));
    index = name.indexOf(":", index + 1);
  }
  if (name !== "") {
    result.push(name);
  }
  return result;
}

/**
 * Get all non-leaf accounts for the given accounts.
 * @param accounts - account names.
 */
export function get_internal_accounts(accounts: Iterable<string>): string[] {
  const res = new Set<string>();
  for (const account of accounts) {
    let index = account.indexOf(":");
    while (index !== -1) {
      res.add(account.slice(0, index));
      index = account.indexOf(":", index + 1);
    }
  }
  return sort(res);
}

const is_true = () => true;

/**
 * Get a predicate to check whether another account is equal to or a descendant of the given one.
 * @param name - an account name.
 */
export function is_descendant_or_equal(
  name: string,
): (other: string) => boolean {
  if (name === "") {
    return is_true;
  }
  const prefix = `${name}:`;
  return (other) => other === name || other.startsWith(prefix);
}

/**
 * Get a predicate to check whether another account a descendant of the given one.
 * @param name - an account name.
 */
export function is_descendant(name: string): (other: string) => boolean {
  if (name === "") {
    return (other) => other.length > 0;
  }
  const prefix = `${name}:`;
  return (other) => other.startsWith(prefix);
}
