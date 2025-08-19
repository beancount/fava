/**
 * Get the basename of a file path.
 */
export function basename(filename: string): string {
  const parts = filename.split(/\/|\\/);
  return parts[parts.length - 1] ?? "";
}

/**
 * Get the extension of a filename.
 */
export function ext(filename: string): string {
  const match = /\.(\w+)$/.exec(filename);
  return match?.[1] ?? "";
}

/**
 * Check whether the given filename includes the account parts at the end.
 */
export function documentHasAccount(filename: string, account: string): boolean {
  const accountParts = account.split(":").reverse();
  const folders = filename.split(/\/|\\/).reverse().slice(1);
  return accountParts.every((part, index) => part === folders[index]);
}

/**
 * Splits the path to dirname (including last separator) and basename. Keeps
 * Windows and UNIX style path separators as they are, but handles both.
 */
export function dirnameBasename(path: string): [string, string] {
  // Special case for when we only have the last remaining separator i.e. root
  if (path.length < 2) {
    return ["", path];
  }
  // Handle both Windows and unix style path separators and a mixture of them
  const lastIndexOfSlash = path.lastIndexOf("/", path.length - 2);
  const lastIndexOfBackslash = path.lastIndexOf("\\", path.length - 2);
  const lastIndex =
    lastIndexOfSlash > lastIndexOfBackslash
      ? lastIndexOfSlash
      : lastIndexOfBackslash;
  // This could maybe happen on Windows if the path name is something like C:\
  if (lastIndex < 0) {
    return ["", path];
  }
  return [path.substring(0, lastIndex + 1), path.substring(lastIndex + 1)];
}
