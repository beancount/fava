import { LanguageSupport, StreamLanguage } from "@codemirror/language";

import { bqlCompletion } from "./bql-autocomplete.ts";
import { bqlStreamParser } from "./bql-stream-parser.ts";

const bqlLanguage = StreamLanguage.define(bqlStreamParser);

export const bql = new LanguageSupport(
  bqlLanguage,
  bqlLanguage.data.of({
    autocomplete: bqlCompletion,
  }),
);
