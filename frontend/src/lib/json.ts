import type { Result } from "./result.ts";
import { err, ok } from "./result.ts";

/**
 * Parse a JSON string into an object.
 */
export function parseJSON(data: string): Result<unknown, SyntaxError> {
  try {
    return ok(JSON.parse(data));
  } catch (error) {
    if (error instanceof SyntaxError) {
      return err(error);
    }
    throw error;
  }
}
