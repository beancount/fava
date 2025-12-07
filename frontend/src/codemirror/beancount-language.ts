import {
  defineLanguageFacet,
  Language,
  languageDataProp,
  LanguageSupport,
  syntaxHighlighting,
} from "@codemirror/language";
import { highlightTrailingWhitespace, keymap } from "@codemirror/view";
import { styleTags, tags } from "@lezer/highlight";
import { Language as TSLanguage, Parser as TSParser } from "web-tree-sitter";

import ts_wasm from "../../node_modules/web-tree-sitter/tree-sitter.wasm";
import { beancount_completion } from "./beancount-autocomplete.ts";
import { beancount_fold } from "./beancount-fold.ts";
import { beancount_format } from "./beancount-format.ts";
import { beancount_highlight } from "./beancount-highlight.ts";
import { beancount_indent } from "./beancount-indent.ts";
// WASM build of tree-sitter grammar from https://github.com/yagebu/tree-sitter-beancount
import ts_beancount_wasm from "./tree-sitter-beancount.wasm";
import { LezerTSParser } from "./tree-sitter-parser.ts";

/** Import the tree-sitter and Beancount language WASM files and initialise the parser. */
async function load_beancount_parser(): Promise<TSParser> {
  const ts = import.meta.resolve(ts_wasm);
  const ts_beancount = import.meta.resolve(ts_beancount_wasm);
  await TSParser.init({ locateFile: () => ts });
  const lang = await TSLanguage.load(ts_beancount);
  const parser = new TSParser();
  parser.setLanguage(lang);
  return parser;
}

const beancount_language_facet = defineLanguageFacet();
const beancount_language_support_extensions = [
  beancount_fold,
  syntaxHighlighting(beancount_highlight),
  beancount_indent,
  keymap.of([{ key: "Control-d", mac: "Meta-d", run: beancount_format }]),
  beancount_language_facet.of({
    autocomplete: beancount_completion,
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
    type.isTop ? beancount_language_facet : undefined,
  ),
];

const ts_parser = await load_beancount_parser();

export const beancount_language_support = new LanguageSupport(
  new Language(
    beancount_language_facet,
    new LezerTSParser(ts_parser, props, "beancount_file"),
    [],
    "beancount",
  ),
  beancount_language_support_extensions,
);
