import { join } from "path";

import { test } from "uvu";
import assert from "uvu/assert";
import TSParser from "web-tree-sitter";

import { LezerTSParser } from "../src/codemirror/tree-sitter-parser";

async function load(): Promise<TSParser> {
  await TSParser.init();
  const path = join(
    __dirname,
    "..",
    "src",
    "codemirror",
    "tree-sitter-beancount.wasm",
  );
  const lang = await TSParser.Language.load(path);
  const parser = new TSParser();
  parser.setLanguage(lang);
  return parser;
}

test("parse a single price directive", async () => {
  const ts_parser = await load();
  const parser = new LezerTSParser(ts_parser, [], "beancount_file");
  const tree = parser.parse("2012-12-12 price USD 1 EUR\n");
  assert.snapshot(
    // eslint-disable-next-line @typescript-eslint/no-base-to-string
    tree.toString(),
    "beancount_file(price(date,PRICE,currency,amount(number,currency)))",
  );
});

test.run();
