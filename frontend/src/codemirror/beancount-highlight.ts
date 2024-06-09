import { HighlightStyle } from "@codemirror/language";
import { tags } from "@lezer/highlight";

export const beancountEditorHighlight = HighlightStyle.define([
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
    color: "var(--editor-currencies)",
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
    // Tag, link
    tag: tags.labelName,
    color: "var(--editor-label-name)",
  },
  {
    // Currency value
    tag: tags.number,
    color: "var(--editor-number)",
  },
  {
    // Payee, Narration
    tag: tags.string,
    color: "var(--editor-string)",
  },
  {
    // Invalid token
    tag: tags.invalid,
    color: "var(--editor-invalid)",
    backgroundColor: "var(--editor-invalid-background)",
  },
]);

export const beancountQueryHighlight = HighlightStyle.define([
  {
    // Keywords: Select, Where, And
    tag: tags.keyword,
    color: "var(--bql-keywords)",
  },
  {
    // Values
    tag: [
      tags.typeName,
      tags.className,
      tags.number,
      tags.changed,
      tags.annotation,
      tags.modifier,
      tags.self,
      tags.namespace,
    ],
    color: "var(--bql-values)",
  },
  {
    // Strings
    tag: [tags.processingInstruction, tags.string, tags.inserted],
    color: "var(--bql-string)",
  },
  {
    // Errors
    tag: [
      tags.name,
      tags.deleted,
      tags.character,
      tags.propertyName,
      tags.macroName,
    ],
    color: "var(--bql-errors)",
  },
]);
