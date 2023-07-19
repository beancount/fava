import { LanguageSupport, StreamLanguage } from "@codemirror/language";

import { bqlCompletion } from "./bql-autocomplete";
import { bqlStreamParser } from "./bql-stream-parser";

const bqlLanguage = StreamLanguage.define(bqlStreamParser);

export const bql = new LanguageSupport(
  bqlLanguage,
  bqlLanguage.data.of({
    autocomplete: bqlCompletion,
  }),
);
