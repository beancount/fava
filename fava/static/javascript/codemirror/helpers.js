import CodeMirror from 'codemirror/lib/codemirror';
import fuzzy from 'fuzzyjs';

export function getCurrentWord(cursor, line) {
  return line.slice(0, cursor.ch).match(/(\S*)$/)[0];
}

export function fuzzyMatch(cursor, currentWord, completions) {
  const search = currentWord.toLowerCase();
  return {
    list: fuzzy.filter(search, completions, {}),
    from: new CodeMirror.Pos(cursor.line, cursor.ch - currentWord.length),
    to: cursor,
  };
}
