import { readFile } from "fs/promises";
import { join } from "path";

import { parseJSON } from "../src/lib/json";

/** Load the Python test snapshot output with the given name and parse as JSON. */
export async function loadJSONSnapshot(
  name: `${string}.json`,
): Promise<unknown> {
  const path = join(__dirname, "..", "..", "tests", "__snapshots__", name);
  return parseJSON(await readFile(path, "utf8")).unwrap();
}
