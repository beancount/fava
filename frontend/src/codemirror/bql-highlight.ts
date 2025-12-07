import { HighlightStyle } from "@codemirror/language";
import { tags } from "@lezer/highlight";

export const bql_highlight = HighlightStyle.define([
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
