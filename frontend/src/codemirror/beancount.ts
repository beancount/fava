import { HighlightStyle, tags } from "@codemirror/highlight";
import { LanguageSupport } from "@codemirror/language";
import { StreamLanguage } from "@codemirror/stream-parser";

import { beancountCompletion } from "./beancount-autocomplete";
import { beancountFold } from "./beancount-fold";
import { beancountStreamParser } from "./beancount-stream-parser";

const beancountLanguage = StreamLanguage.define(beancountStreamParser);

const beancountHighlight = HighlightStyle.define(
  {
    // Dates
    tag: tags.special(tags.number),
    color: "var(--color-editor-date)",
  },
  {
    // Strings
    tag: tags.string,
    color: "#a11",
  },
  {
    // Accounts
    tag: tags.className,
    color: "var(--color-editor-account)",
  },
  {
    // Plain comments
    tag: tags.comment,
    color: "var(--color-editor-comment)",
  },
  {
    // Sections
    tag: tags.special(tags.lineComment),
    color: "var(--color-editor-comment)",
    border: "solid 1px var(--color-editor-comment)",
    borderRadius: "2px",
    paddingRight: "10px",
    fontWeight: "500",
  },
  {
    // Currencies
    tag: tags.unit,
    color: "#708",
  },
  {
    // Directives
    tag: tags.keyword,
    fontWeight: "500",
    color: "var(--color-editor-directive)",
  },
  {
    // Tags and links
    tag: tags.labelName,
    color: "#219",
  },
  {
    // Option name
    tag: tags.special(tags.string),
    color: "var(--color-editor-class)",
  },
  {
    // Invalid token
    tag: tags.invalid,
    color: "var(--color-editor-invalid)",
  },
  {
    // Trailing whitespace
    tag: tags.special(tags.invalid),
    backgroundColor: "var(--color-editor-trailing-whitespace)",
  }
);

export const beancount = new LanguageSupport(beancountLanguage, [
  beancountFold,
  beancountHighlight,
  beancountLanguage.data.of({
    autocomplete: beancountCompletion,
  }),
]);
