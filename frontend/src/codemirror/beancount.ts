import {
  defineLanguageFacet,
  Language,
  languageDataProp,
  LanguageSupport,
  syntaxHighlighting,
} from "@codemirror/language";
import { highlightTrailingWhitespace, keymap } from "@codemirror/view";
import { styleTags, tags } from "@lezer/highlight";
import TSParser from "web-tree-sitter";
import ts_wasm from "web-tree-sitter/tree-sitter.wasm";

import { beancountCompletion } from "./beancount-autocomplete";
import { beancountFold } from "./beancount-fold";
import { beancountFormat } from "./beancount-format";
import { beancountEditorHighlight } from "./beancount-highlight";
import { beancountIndent } from "./beancount-indent";
// WASM build of tree-sitter grammar from https://github.com/yagebu/tree-sitter-beancount
import ts_beancount_wasm from "./tree-sitter-beancount.wasm";
import { LezerTSParser } from "./tree-sitter-parser";

/** Import the tree-sitter and Beancount language WASM files and initialise the parser. */
async function loadBeancountParser(): Promise<TSParser> {
  const ts = import.meta.resolve(ts_wasm);
  const ts_beancount = import.meta.resolve(ts_beancount_wasm);
  await TSParser.init({ locateFile: () => ts });
  const lang = await TSParser.Language.load(ts_beancount);
  const parser = new TSParser();
  parser.setLanguage(lang);
  return parser;
}

const beancountLanguageFacet = defineLanguageFacet();
const beancountLanguageSupportExtensions = [
  beancountFold,
  syntaxHighlighting(beancountEditorHighlight),
  beancountIndent,
  keymap.of([{ key: "Control-d", mac: "Meta-d", run: beancountFormat }]),
  beancountLanguageFacet.of({
    autocomplete: beancountCompletion,
    commentTokens: { line: ";" },
    indentOnInput: /^\s+\d\d\d\d/,
  }),
  highlightTrailingWhitespace(),
];

/** The node props that allow for highlighting/coloring of the code. */
const props = [
  styleTags({
    account: tags.className,
    currency: tags.unit,
    date: tags.special(tags.number),
    string: tags.string,
    "BALANCE CLOSE COMMODITY CUSTOM DOCUMENT EVENT NOTE OPEN PAD PRICE TRANSACTION QUERY":
      tags.keyword,
    "tag link": tags.labelName,
    number: tags.number,
    key: tags.propertyName,
    bool: tags.bool,
    "PUSHTAG POPTAG PUSHMETA POPMETA OPTION PLUGIN INCLUDE": tags.standard(
      tags.string,
    ),
  }),
  languageDataProp.add((type) =>
    type.isTop ? beancountLanguageFacet : undefined,
  ),
];

/** Only load the TSParser once. */
let load_parser: Promise<TSParser> | null = null;

/**
 * Get the LanguageSupport for Beancount.
 *
 * Since this might need to load the tree-sitter parser, this is async.
 */
export async function getBeancountLanguageSupport(): Promise<LanguageSupport> {
  if (!load_parser) {
    load_parser = loadBeancountParser();
  }
  const ts_parser = await load_parser;
  return new LanguageSupport(
    new Language(
      beancountLanguageFacet,
      new LezerTSParser(ts_parser, props, "beancount_file"),
      [],
      "beancount",
    ),
    beancountLanguageSupportExtensions,
  );
}
