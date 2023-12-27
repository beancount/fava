import { HighlightStyle } from "@codemirror/language";
import { tags } from "@lezer/highlight";

export const beancountHighlight = HighlightStyle.define([
  {
    // Dates
    tag: tags.special(tags.number),
    color: "var(--editor-date)",
  },
  {
    // Accounts
    tag: tags.className,
    color: "var(--editor-account)",
  },
  {
    // Plain comments
    tag: tags.comment,
    color: "var(--editor-comment)",
  },
  {
    // Sections
    tag: tags.special(tags.lineComment),
    color: "var(--editor-comment)",
    border: "solid 1px var(--editor-comment)",
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
    color: "var(--editor-directive)",
  },
  {
    // Option name
    tag: tags.standard(tags.string),
    color: "var(--editor-class)",
  },
  {
    // Invalid token
    tag: tags.invalid,
    color: "var(--editor-invalid)",
    backgroundColor: "var(--editor-invalid-background)",
  },
]);
