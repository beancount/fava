import CodeMirror, { Position } from "codemirror";

import { fuzzyfilter } from "../lib/fuzzy";

export function getCurrentWord(cursor: Position, line: string): string {
  const lineUpToCursor = line.slice(0, cursor.ch);
  return /(\S*)$/.exec(lineUpToCursor)?.[0] || "";
}

export function fuzzyMatch(
  cursor: Position,
  currentWord: string,
  completions: string[]
): { list: string[]; from: Position; to: Position } {
  return {
    list: fuzzyfilter(currentWord, completions),
    from: new CodeMirror.Pos(cursor.line, cursor.ch - currentWord.length),
    to: cursor,
  };
}
