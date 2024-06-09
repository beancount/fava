/** Render the message of an error, with causes if set. */
export function errorWithCauses(error: Error): string {
  const msg = error.message;
  return error.cause instanceof Error
    ? `${msg}\n  Caused by: ${errorWithCauses(error.cause)}`
    : error.message;
}
