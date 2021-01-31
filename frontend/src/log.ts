/**
 * Log various errors
 *
 * In the future, this might turn into a noop for production builds.
 * @param error
 */
export function log_error(...args: unknown[]): void {
  // eslint-disable-next-line no-console
  console.error(...args);
}
