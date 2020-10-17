import CodeMirror, { Editor } from "codemirror";

import { getCompletion } from "../stores";

import { fuzzyMatch, getCurrentWord } from "./helpers";

const completionSources = {
  undatedDirectives: ["option", "plugin", "include"],
  datedDirectives: [
    "open",
    "close",
    "commodity",
    "balance",
    "pad",
    "note",
    "document",
    "price",
    "event",
    "query",
  ],
};

const directiveCompletions: Record<
  string,
  Array<"accounts" | "currencies" | null>
> = {
  open: ["accounts", "currencies"],
  close: ["accounts"],
  commodity: ["currencies"],
  balance: ["accounts", null, "currencies"],
  pad: ["accounts", "accounts"],
  note: ["accounts"],
  document: ["accounts"],
  price: ["currencies", null, "currencies"],
};

CodeMirror.registerHelper("hint", "beancount", (cm: Editor) => {
  const doc = cm.getDoc();
  const cursor = doc.getCursor();
  const line = doc.getLine(cursor.line);
  const token = cm.getTokenAt(cursor);
  const currentCharacter = line[cursor.ch - 1];
  const currentWord = getCurrentWord(cursor, line);

  // If '#' or '^' has just been typed, there won't be a tag or link token yet
  if (currentCharacter === "#" || currentCharacter === "^") {
    const list =
      currentCharacter === "#" ? getCompletion("tags") : getCompletion("links");
    return {
      list,
      from: cursor,
      to: cursor,
    };
  }

  if (token.type === "tag" || token.type === "link") {
    const list =
      token.type === "tag" ? getCompletion("tags") : getCompletion("links");
    return {
      list: list.filter((d) => d.startsWith(currentWord.slice(1))),
      from: new CodeMirror.Pos(cursor.line, token.start + 1),
      to: new CodeMirror.Pos(cursor.line, token.end),
    };
  }

  // directives at the start of the line
  if (currentWord === line && line.length > 0) {
    return {
      list: completionSources.undatedDirectives.filter((d) =>
        d.startsWith(currentWord)
      ),
      from: new CodeMirror.Pos(cursor.line, 0),
      to: cursor,
    };
  }

  const lineTokens = cm.getLineTokens(cursor.line);

  if (lineTokens.length > 0) {
    const startCurrentWord = cursor.ch - currentWord.length;
    const previousTokens = lineTokens.filter((d) => d.end <= startCurrentWord);

    // complete accounts for indented lines
    if (lineTokens[0].type === "whitespace") {
      if (previousTokens.length === 1) {
        return fuzzyMatch(cursor, currentWord, getCompletion("accounts"));
      }
    }

    // dated directives
    if (lineTokens[0].type === "date") {
      // date whitespace -> complete directives
      if (previousTokens.length === 2) {
        return {
          list: completionSources.datedDirectives.filter((d) =>
            d.startsWith(currentWord)
          ),
          from: new CodeMirror.Pos(cursor.line, cursor.ch - currentWord.length),
          to: cursor,
        };
      }

      // Ignore negative sign from previousTokens
      const tokenLength = previousTokens.filter((t) => t.type != null).length;
      if (tokenLength % 2 === 0) {
        const directiveType = previousTokens[2].string;
        if (directiveType in directiveCompletions) {
          const complType =
            directiveCompletions[directiveType][tokenLength / 2 - 2];
          if (complType) {
            return fuzzyMatch(cursor, currentWord, getCompletion(complType));
          }
        }
      }
    }
  }

  return {
    list: [],
  };
});
