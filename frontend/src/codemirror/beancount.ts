import { indentUnit, LanguageSupport } from "@codemirror/language";
import { Prec } from "@codemirror/state";
import { StreamLanguage } from "@codemirror/stream-parser";
import { keymap } from "@codemirror/view";

import { beancountCompletion } from "./beancount-autocomplete";
import { beancountFold } from "./beancount-fold";
import { beancountFormat } from "./beancount-format";
import { beancountHighlight } from "./beancount-highlight";
import { beancountIndent } from "./beancount-indent";
import { beancountStreamParser } from "./beancount-stream-parser";

const beancountLanguage = StreamLanguage.define(beancountStreamParser);

export const beancount = new LanguageSupport(beancountLanguage, [
  beancountFold,
  beancountHighlight,
  beancountIndent,
  keymap.of([{ key: "Control-d", mac: "Meta-d", run: beancountFormat }]),
  Prec.fallback(indentUnit.of("  ")),
  beancountLanguage.data.of({
    indentOnInput: /^\s+\d\d\d\d/,
    autocomplete: beancountCompletion,
  }),
]);
