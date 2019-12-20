/**
 * Data validation.
 *
 * These functions allow us to ensure that `unknown` data obtained from, e.g.,
 * an API, is of a specified type.
 */

class ValidationError extends Error {}

/**
 * A validator.
 *
 * That is, a function that checks an unknown object to be of a specified type
 * or throw an error otherwise.
 */
export interface Validator<T> {
  (json: unknown): T;
}

/**
 * Validate as unknown (noop).
 */
export function unknown(json: unknown): unknown {
  return json;
}

/**
 * Validate a string.
 */
export function string(json: unknown): string {
  if (typeof json === "string") {
    return json;
  }
  throw new ValidationError(`Expected a string, got '${json}' instead.`);
}

/**
 * Validate a boolean.
 */
export function boolean(json: unknown): boolean {
  if (typeof json === "boolean") {
    return json;
  }
  throw new ValidationError(`Expected a boolean, got '${json}' instead.`);
}

/**
 * Validate a number.
 */
export function number(json: unknown): number {
  if (typeof json === "number") {
    return json;
  }
  throw new ValidationError(`Expected a number, got '${json}' instead.`);
}

/**
 * Validate a date (from a string).
 */
export function date(json: unknown): Date {
  if (typeof json === "string" || json instanceof Date) {
    return new Date(json);
  }
  throw new ValidationError(`Expected a date: ${json}`);
}

/**
 * Validate a value to be equal to a constant value.
 */
export function constant<T>(value: T): Validator<T> {
  return (json: unknown) => {
    if (json === value) {
      return json as T;
    }
    throw new ValidationError(`Expected a constant: ${json}`);
  };
}

/**
 * Validate a value that is of one of two given types.
 */
export function union<A, B>(
  a: Validator<A>,
  b: Validator<B>
): Validator<A | B> {
  return (json: unknown) => {
    for (const validator of [a, b]) {
      try {
        return validator(json);
      } catch (exc) {
        // pass
      }
    }
    throw new ValidationError(`Validating union failed`);
  };
}

/**
 * Validator for an object that might be undefined.
 */
export function optional<T>(validator: Validator<T>): Validator<T | undefined> {
  return (json: unknown) => {
    return json === undefined ? undefined : validator(json);
  };
}

/**
 * Lazy validator to allow for recursive structures.
 */
export function lazy<T>(func: () => Validator<T>): Validator<T> {
  return (json: unknown) => {
    return func()(json);
  };
}

/**
 * Validator for an array of values.
 */
export function array<T>(validator: Validator<T>): Validator<T[]> {
  return (json: unknown) => {
    if (Array.isArray(json)) {
      const result: T[] = [];
      json.forEach(element => {
        result.push(validator(element));
      });
      return result;
    }
    throw new ValidationError(`Expected an array: ${json}`);
  };
}

/**
 * Validator for a tuple of fixed length.
 */
export function tuple<A, B>(
  decoders: [Validator<A>, Validator<B>]
): Validator<[A, B]> {
  return (json: unknown) => {
    if (Array.isArray(json) && json.length === 2) {
      const result = [];

      for (let i = 0; i < decoders.length; i += 1) {
        result[i] = decoders[i](json[i]);
      }
      return result as [A, B];
    }
    throw new ValidationError(`Expected a tuple: ${json}`);
  };
}

const isJsonObject = (json: unknown): json is Record<string, unknown> =>
  typeof json === "object" && json !== null && !Array.isArray(json);

/**
 * Validator for an object with some given properties.
 */
export function object<T>(
  validators: { [t in keyof T]: Validator<T[t]> }
): Validator<T> {
  return (json: unknown) => {
    if (isJsonObject(json)) {
      const obj: Partial<T> = {};
      // eslint-disable-next-line no-restricted-syntax
      for (const key in validators) {
        if (Object.prototype.hasOwnProperty.call(validators, key)) {
          obj[key] = validators[key](json[key]);
        }
      }
      return obj as T;
    }
    throw new ValidationError();
  };
}

/**
 * Validator for a dict-like structure.
 */
export function record<T>(decoder: Validator<T>): Validator<Record<string, T>> {
  return (json: unknown) => {
    if (isJsonObject(json)) {
      const ret: Record<string, T> = {};
      // eslint-disable-next-line no-restricted-syntax
      for (const key in json) {
        if (Object.prototype.hasOwnProperty.call(json, key)) {
          ret[key] = decoder(json[key]);
        }
      }
      return ret;
    }
    throw new ValidationError();
  };
}
