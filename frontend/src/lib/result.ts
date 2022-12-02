/**
 * Result types to allow for more Typescript-friendly
 * catching of errors and exceptions.
 */

/** A successful result. */
export interface Ok<T> {
  success: true;
  value: T;
}
/** An error result. */
export interface Err<E> {
  success: false;
  value: E;
}
/** Result of an operation that might fail */
export type Result<T, E> = Ok<T> | Err<E>;

/** Wrap the value in a successful result. */
export function ok<T>(value: T): Ok<T> {
  return { success: true, value };
}

/** Wrap the value in an error result. */
export function err<E>(value: E): Err<E> {
  return { success: false, value };
}
