import {
  indentOnInput,
  indentUnit,
  LanguageSupport,
} from "@codemirror/language";
import { Prec } from "@codemirror/state";
import { StreamLanguage } from "@codemirror/stream-parser";

import { beancountCompletion } from "./beancount-autocomplete";
import { beancountFold } from "./beancount-fold";
import { beancountHighlight } from "./beancount-highlight";
import { beancountIndent } from "./beancount-indent";
import { beancountStreamParser } from "./beancount-stream-parser";

const beancountLanguage = StreamLanguage.define(beancountStreamParser);

export const beancount = new LanguageSupport(beancountLanguage, [
  beancountFold,
  beancountHighlight,
  beancountIndent,
  Prec.fallback(indentUnit.of("  ")),
  indentOnInput(),
  beancountLanguage.data.of({
    indentOnInput: /^\s+\d\d\d\d/,
    autocomplete: beancountCompletion,
  }),
]);
