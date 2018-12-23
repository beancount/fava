import CodeMirror from "codemirror";

import { fuzzyMatch, getCurrentWord } from "./helpers";
import { columns, functions, keywords } from "./bql-grammar.json";

const functionCompletions = functions.map(f => `${f}(`);
const commands = ["select"];

CodeMirror.registerHelper("hint", "beancount-query", cm => {
  const cursor = cm.getCursor();
  const line = cm.getLine(cursor.line);
  const currentWord = getCurrentWord(cursor, line);

  // keywords at the start of the line
  if (currentWord === line) {
    return {
      list: commands.filter(d => d.startsWith(currentWord)),
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
