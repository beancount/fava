import {
  LanguageSupport,
  StreamLanguage,
  syntaxHighlighting,
} from "@codemirror/language";

import { bql_completion } from "./bql-autocomplete.ts";
import { bql_highlight } from "./bql-highlight.ts";
import { bql_stream_parser } from "./bql-stream-parser.ts";

const bql_language = StreamLanguage.define(bql_stream_parser);

export const bql_language_support = new LanguageSupport(bql_language, [
  bql_language.data.of({
    autocomplete: bql_completion,
  }),
  syntaxHighlighting(bql_highlight),
]);
