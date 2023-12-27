/**
 * Log various errors
 *
 * In the future, this might turn into a noop for production builds.
 */
export function log_error(...args: unknown[]): void {
  // eslint-disable-next-line no-console
  console.error(...args);
}

/**
 * Assert some condition.
 *
 * In the future, this might turn into a noop for production builds.
 */
export function assert(
  condition: boolean,
  message: string,
  ...extraArgs: unknown[]
): void {
  // eslint-disable-next-line no-console
  console.assert(condition, message, ...extraArgs);
}
