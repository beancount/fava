import { indentService } from "@codemirror/language";

export const beancountIndent = indentService.of((context, pos) => {
  const textAfterPos = context.textAfterPos(pos);
  if (/^\s*\d\d\d\d/.exec(textAfterPos)) {
    // Lines starting with a date should not be indented.
    return 0;
  }
  const line = context.state.doc.lineAt(pos);
  if (/^\s+\S+/.exec(line.text) ?? /^\d\d\d\d/.exec(line.text)) {
    // The previous (or this one?) line was indented.
    return context.unit;
  }
  return 0;
});
