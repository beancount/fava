import { LanguageSupport } from "@codemirror/language";
import { StreamLanguage } from "@codemirror/stream-parser";

import { beancountCompletion } from "./beancount-autocomplete";
import { beancountFold } from "./beancount-fold";
import { beancountStreamParser } from "./beancount-stream-parser";

const beancountLanguage = StreamLanguage.define(beancountStreamParser);

export const beancount = new LanguageSupport(beancountLanguage, [
  beancountFold,
  beancountLanguage.data.of({
    autocomplete: beancountCompletion,
  }),
]);
