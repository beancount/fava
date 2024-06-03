/**
 * Data validation.
 *
 * These functions allow us to ensure that `unknown` data obtained from, e.g.,
 * an API, is of a specified type.
 */

import type { Ok, Result } from "./result";
import { err, ok } from "./result";

/**
 * A validator.
 *
 * That is, a function that checks an unknown object to be of a specified type.
 */
export type Validator<T> = (json: unknown) => Result<T, string>;
/** A validator that will never error. */
export type SafeValidator<T> = (json: unknown) => Ok<T>;

/** Extract the validated type. */
export type ValidationT<R> = R extends Validator<infer T> ? T : never;

/**
 * Validate with a default value if validation fails.
 */
export function defaultValue<T>(
  validator: Validator<T>,
  value: () => T,
): SafeValidator<T> {
  return (json) => {
    const res = validator(json);
    return res.is_ok ? res : ok(value());
  };
}

/**
 * Validate as unknown (noop, just wrap in ok()).
 */
export const unknown: SafeValidator<unknown> = ok;

/**
 * Validate a string.
 */
export const string: Validator<string> = (json) =>
  typeof json === "string" ? ok(json) : err("string validation failed.");

/** Validate a string and return the empty string on failure. */
export const optional_string: SafeValidator<string> = (json) =>
  typeof json === "string" ? ok(json) : ok("");

/**
 * Validate a boolean.
 */
export const boolean: Validator<boolean> = (json) =>
  typeof json === "boolean" ? ok(json) : err("boolean validation failed.");

/**
 * Validate a number.
 */
export const number: Validator<number> = (json) =>
  typeof json === "number" ? ok(json) : err("number validation failed.");

/**
 * Validate a date (from a string).
 */
export const date: Validator<Date> = (json) => {
  if (json instanceof Date) {
    return ok(json);
  }
  if (typeof json === "string") {
    if (json.length !== 10) {
      return err("Expected date to be a string of length 10");
    }
    const parsed = new Date(json);
    if (Number.isNaN(+parsed)) {
      return err("Expected a date");
    }
    return ok(parsed);
  }
  return err("Expected date to be a string or Date");
};

/**
 * Validate a value to be equal to a constant value.
 */
export function constant<T extends null | boolean | string | number>(
  value: T,
): Validator<T> {
  return (json) =>
    json === value ? ok(json as T) : err("Expected a constant");
}

/** Helper type to get the union of the types in a tuple. */
type TupleElement<T extends unknown[]> = T extends (infer E)[] ? E : T;

/**
 * Validate a value is one of the provided constant values.
 */
export function constants<const T extends (null | boolean | string | number)[]>(
  ...args: T
): Validator<TupleElement<T>> {
  return (json) =>
    args.includes(json as null | boolean | string | number)
      ? ok(json as TupleElement<T>)
      : err("Expected a constant");
}

/**
 * Validate a value that is of one of the given types.
 */
export function union<T extends unknown[]>(
  ...args: { [P in keyof T]: Validator<T[P]> }
): Validator<TupleElement<T>> {
  return (json) => {
    for (const validator of args) {
      const res = validator(json) as Result<TupleElement<T>, string>;
      if (res.is_ok) {
        return res;
      }
    }
    return err("Validating union failed");
  };
}

/**
 * Validator for an object that might be null or undefined.
 */
export function optional<T>(validator: Validator<T>): Validator<T | null> {
  return (json) => (json == null ? ok(null) : validator(json));
}

/**
 * Lazy validator to allow for recursive structures.
 */
export function lazy<T>(func: () => Validator<T>): Validator<T> {
  return (json) => func()(json);
}

/**
 * Validator for an array of values.
 */
export function array<T>(validator: Validator<T>): Validator<T[]> {
  return (json) => {
    if (Array.isArray(json)) {
      const result: T[] = [];
      for (const element of json) {
        const res = validator(element);
        if (res.is_ok) {
          result.push(res.value);
        } else {
          return res;
        }
      }
      return ok(result);
    }
    return err("array validation failed");
  };
}

/**
 * Validator for a tuple of fixed length.
 */
export function tuple<const T extends unknown[]>(
  ...args: { [P in keyof T]: Validator<T[P]> }
): Validator<T> {
  return (json) => {
    if (Array.isArray(json) && json.length === args.length) {
      const result = [];
      let i = 0;
      for (const decoder of args) {
        const res = decoder(json[i]);
        if (res.is_ok) {
          result[i] = res.value;
        } else {
          return res;
        }
        i += 1;
      }
      return ok(result as T);
    }
    return err("Expected a tuple");
  };
}

/**
 * Check whether the given object is a string-indexable object.
 */
export function isJsonObject(json: unknown): json is Record<string, unknown> {
  return typeof json === "object" && json !== null && !Array.isArray(json);
}

/**
 * Validator for an object with some given properties.
 */
export function object<T>(validators: {
  [t in keyof T]: Validator<T[t]>;
}): Validator<T> {
  return (json) => {
    if (isJsonObject(json)) {
      const obj: Partial<T> = {};
      // eslint-disable-next-line no-restricted-syntax
      for (const key in validators) {
        if (Object.hasOwn(validators, key)) {
          const res = validators[key](json[key]);
          if (res.is_ok) {
            obj[key] = res.value;
          } else {
            return err(
              `Validating object failed at key '${key}': ${res.error}`,
            );
          }
        }
      }
      return ok(obj as T);
    }
    return err("Validating object failed");
  };
}

/**
 * Validator for a dict-like structure.
 */
export function record<T>(decoder: Validator<T>): Validator<Record<string, T>> {
  return (json) => {
    if (isJsonObject(json)) {
      const ret: Record<string, T> = {};
      for (const [key, value] of Object.entries(json)) {
        const res = decoder(value);
        if (res.is_ok) {
          ret[key] = res.value;
        } else {
          return err(`Validating record failed at key '${key}': ${res.error}`);
        }
      }
      return ok(ret);
    }
    return err("Validating record failed");
  };
}
