import type { Result } from "./result";
import { err, ok } from "./result";

/**
 * Parse a JSON string into an object.
 */
export function parseJSON(data: string): Result<unknown, "JSON syntax error"> {
  try {
    return ok(JSON.parse(data));
  } catch (error) {
    if (error instanceof SyntaxError) {
      return err("JSON syntax error" as const);
    }
    throw error;
  }
}
