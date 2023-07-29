import type { Result } from "./result";
import { err, ok } from "./result";

/**
 * Parse a JSON string into an object.
 */
export function parseJSON(data: string): Result<unknown, string> {
  try {
    return ok(JSON.parse(data));
  } catch (error) {
    if (error instanceof SyntaxError) {
      return err(`JSON syntax error: ${error.message}`);
    }
    throw error;
  }
}
