import CodeMirror, { Editor } from "codemirror";

import bqlGrammar from "./bql-grammar";
import { fuzzyMatch, getCurrentWord } from "./helpers";

const { columns, functions, keywords } = bqlGrammar;

const functionCompletions = functions.map((f: string) => `${f}(`);
const commands = ["select"];

CodeMirror.registerHelper("hint", "beancount-query", (cm: Editor) => {
  const doc = cm.getDoc();
  const cursor = doc.getCursor();
  const line = doc.getLine(cursor.line);
  const currentWord = getCurrentWord(cursor, line);

  // keywords at the start of the line
  if (currentWord === line) {
    return {
      list: commands.filter((d) => d.startsWith(currentWord)),
      from: new CodeMirror.Pos(cursor.line, 0),
      to: cursor,
    };
  }

  return fuzzyMatch(
    cursor,
    currentWord,
    columns.concat(functionCompletions, keywords)
  );
});
