import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { Language as TSLanguage, Parser as TSParser } from "web-tree-sitter";

import { ledgerDataValidator } from "../src/api/validators.ts";
import { parse_json } from "../src/lib/json.ts";
import { ledger_data } from "../src/stores/index.ts";
import { current_url } from "../src/stores/url.ts";

export const REPOSITORY_ROOT = join(
  fileURLToPath(import.meta.url),
  "..",
  "..",
  "..",
);
const FRONTEND = join(REPOSITORY_ROOT, "frontend");

/** Load the Python test snapshot output with the given name and parse as JSON. */
export async function load_json_snapshot(
  name: `${string}.json`,
): Promise<unknown> {
  const path = join(REPOSITORY_ROOT, "tests", "__snapshots__", name);
  return parse_json(await readFile(path, "utf8")).unwrap();
}

/**
 * Load the tree-sitter parser for Beancount.
 *
 * @param ts - The web-tree-sitter module to use (for a separate instance).
 */
export async function load_beancount_ts_parser(
  ts = { Language: TSLanguage, Parser: TSParser },
): Promise<TSParser> {
  await ts.Parser.init();
  const path = join(
    FRONTEND,
    "src",
    "codemirror",
    "tree-sitter-beancount.wasm",
  );
  const lang = await ts.Language.load(path);
  const parser = new ts.Parser();
  parser.setLanguage(lang);
  return parser;
}

let loaded = false;

/** Load the ledger_data (of the long-example file. */
export async function initialise_ledger_data(): Promise<void> {
  if (loaded) {
    return;
  }
  try {
    const data = await load_json_snapshot(
      "test_internal_api-test_get_ledger_data.json",
    );
    const res = ledgerDataValidator(data).unwrap();
    ledger_data.set(res);
    current_url.set(
      new URL("http://localhost:5000/example-beancount-file/income_statement/"),
    );
    loaded = true;
  } catch (error: unknown) {
    console.error(error);
  }
}
