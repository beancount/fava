import CodeMirror from "codemirror";
import { fuzzytest } from "../helpers";

export function getCurrentWord(cursor, line) {
  return line.slice(0, cursor.ch).match(/(\S*)$/)[0];
}

export function fuzzyMatch(cursor, currentWord, completions) {
  const search = currentWord.toLowerCase();
  return {
    list: completions.filter(completion => fuzzytest(search, completion)),
    from: new CodeMirror.Pos(cursor.line, cursor.ch - currentWord.length),
    to: cursor,
  };
}
