import CodeMirror, { Position } from "codemirror";
import { fuzzytest } from "../helpers";

export function getCurrentWord(cursor: Position, line: string) {
  return line.slice(0, cursor.ch).match(/(\S*)$/)![0];
}

export function fuzzyMatch(
  cursor: Position,
  currentWord: string,
  completions: string[]
) {
  const search = currentWord.toLowerCase();
  return {
    list: completions.filter(completion => fuzzytest(search, completion)),
    from: new CodeMirror.Pos(cursor.line, cursor.ch - currentWord.length),
    to: cursor,
  };
}
