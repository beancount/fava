/**
 * Result types to allow for more type-safe handling of errors.
 *
 * This is basically a partial reimplementation of the Result type in Rust.
 * https://doc.rust-lang.org/std/result/enum.Result.html
 */

interface BaseResult<T, E> {
  /** Whether this is Ok */
  is_ok: boolean;

  /** Whether this is Err */
  is_err: boolean;

  /** Calls op if the result is Ok, otherwise returns the Err value of self. */
  and_then<U>(op: (val: T) => Ok<U>): Result<U, E>;
  and_then<F>(op: (val: T) => Err<F>): Result<T, E | F>;
  and_then<U, F>(op: (val: T) => Result<U, F>): Result<U, E | F>;
  and_then<U, F>(op: (val: T) => Result<U, F>): Result<U, E | F>;

  /** Maps by applying a function to a contained Ok value, leaving Err untouched. */
  map<U>(op: (v: T) => U): Result<U, E>;

  /** Maps by applying a function to a contained Err value, leaving Ok untouched. */
  map_err<F>(op: (v: E) => F): Result<T, F>;

  /** Calls op if the result is Err, otherwise returns the Ok value of self. */
  or_else<F>(op: (v: E) => T): Result<T, F>;

  /** Returns the contained Ok value or throw an Error for Err. */
  unwrap(): T;

  /** Returns the contained Err value or throw an Error for Ok. */
  unwrap_err(): E;

  /** Returns the contained Ok value or a provided default. */
  unwrap_or<U>(d: U): T | U;
}

/** A successful result. */
export class Ok<T> implements BaseResult<T, never> {
  readonly is_ok = true;

  readonly is_err = false;

  constructor(readonly value: T) {}

  and_then<T2>(op: (val: T) => Ok<T2>): Ok<T2>;
  and_then<E2>(op: (val: T) => Err<E2>): Result<T, E2>;
  and_then<T2, E2>(op: (val: T) => Result<T2, E2>): Result<T2, E2>;
  and_then<T2, E2>(op: (val: T) => Result<T2, E2>): Result<T2, E2> {
    return op(this.value);
  }

  map<U>(op: (v: T) => U): Ok<U> {
    return new Ok(op(this.value));
  }

  map_err(): this {
    return this;
  }

  or_else(): this {
    return this;
  }

  unwrap(): T {
    return this.value;
  }

  unwrap_err(): never {
    throw new Error("unwrap_err() called on Ok().");
  }

  unwrap_or(): T {
    return this.value;
  }
}

/** An error result. */
export class Err<E> implements BaseResult<never, E> {
  readonly is_ok = false;

  readonly is_err = true;

  constructor(readonly error: E) {}

  and_then(): this {
    return this;
  }

  map(): this {
    return this;
  }

  or_else<F, U>(op: (v: E) => Result<U, F>): Result<U, F> {
    return op(this.error);
  }

  map_err<F>(op: (v: E) => F): Result<never, F> {
    return new Err(op(this.error));
  }

  unwrap(): never {
    throw new Error("unwrap() called on error.");
  }

  unwrap_err(): E {
    return this.error;
  }

  unwrap_or<U>(val: U): U {
    return val;
  }
}

/** Result of an operation that might fail */
export type Result<T, E> = Ok<T> | Err<E>;

/** Wrap the value in a successful result. */
export function ok<T>(value: T): Ok<T> {
  return new Ok(value);
}

/** Wrap the value in an error result. */
export function err<E>(error: E): Err<E> {
  return new Err(error);
}

/** Collect an array of results into a single result. */
export function collect<T, E>(items: Result<T, E>[]): Result<T[], E> {
  const ok_values: T[] = [];
  for (const r of items) {
    if (r.is_ok) {
      ok_values.push(r.value);
    } else {
      return r;
    }
  }
  return ok(ok_values);
}
