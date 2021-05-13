import type { StreamParser } from "@codemirror/stream-parser";

import accountRegex from "./account-regex";

// The rules should mirror `parser/lexel.l` in beancount
const sectionComment = /^\*.*/;
const comment = /^[#*;].*/;
const inlineComment = /^;.*/;
const string = /^"(?:[^\\]|\\.)*?"/;
const openString = /^"(?:[^\\]|\\.)*?$/;
const closeString = /^(?:[^\\]|\\.)*?"/;
const tag = /^#[A-Za-z0-9\-_/.]+/;
const commodity = /^[A-Z][A-Z0-9'._-]+[A-Z0-9]/;
const bool = /^TRUE|FALSE/;
const date = /^[0-9]{4,}[-/][0-9]+[-/][0-9]+/;
const number = /^-?(?:[0-9]+|[0-9][0-9,]+[0-9])(?:\.[0-9]*)?/;
const txn = /^([*!&#?%PSTCURM]|txn)/;
const undatedDirectives =
  /^(pushtag|poptag|pushmeta|popmeta|option|plugin|include)/;
const directives =
  /^(balance|open|close|commodity|pad|event|custom|price|note|query|document)/;
const link = /^\^[A-Za-z0-9\-_/.]+/;
const meta = /^[a-z][a-zA-Z0-9\-_]+:/;

export const beancountStreamParser: StreamParser<{ string: boolean }> = {
  startState: () => ({ string: false }),
  token(stream, state) {
    if (state.string) {
      if (stream.match(closeString)) {
        state.string = false;
        return "string";
      }
      stream.skipToEnd();
      return "string";
    }
    if (stream.match(/\s+$/)) {
      return "invalid.special";
    }
    if (stream.eatSpace() || stream.eol()) {
      return null;
    }
    const sol = stream.sol();
    if (sol && stream.match(sectionComment)) {
      return "lineComment.special";
    }
    if (sol && stream.match(comment)) {
      return "lineComment";
    }
    if (stream.match(tag) || stream.match(link)) {
      return "labelName";
    }
    if (stream.match(commodity)) {
      return "unit";
    }
    if (stream.match(meta)) {
      return "propertyName";
    }
    if (
      (sol && stream.match(undatedDirectives)) ||
      stream.match(directives) ||
      stream.match(txn)
    ) {
      return "keyword";
    }
    if (stream.match(inlineComment)) {
      return "comment";
    }
    if (stream.match(date)) {
      return "number.special";
    }
    if (stream.match(number)) {
      return "number";
    }
    if (stream.match(bool)) {
      return "bool";
    }
    if (stream.match(string)) {
      if (stream.start === 7 && stream.string.startsWith("option ")) {
        // Option name
        return "string.standard";
      }
      return "string";
    }
    if (stream.match(openString)) {
      state.string = true;
      return "string.special";
    }
    if (stream.match(accountRegex)) {
      return "className";
    }

    // Skip one character since no known token matched.
    const char = stream.next();
    if (char === "@") {
      return "operator";
    }
    if (char === "{" || char === "}") {
      return "bracket";
    }
    stream.skipToEnd();
    return null;
  },
  languageData: {
    commentTokens: { line: ";" },
  },
};
