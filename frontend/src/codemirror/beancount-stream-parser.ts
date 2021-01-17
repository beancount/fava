/* eslint-disable no-useless-escape */
// To keep the regular expressions in sync with Beancount, they might contain
// some superfluous escape characters.

import { StreamParser } from "@codemirror/stream-parser";

import accountRegex from "./account-regex";

// The rules should mirror `parser/lexel.l` in beancount
const sectionComment = /\*.*/;
const comment = /[#*;].*/;
const inlineComment = /;.*/;
const string = /"(?:[^\\]|\\.)*?"/;
const tag = /#[A-Za-z0-9\-_\/.]+/;
const commodity = /[A-Z][A-Z0-9'\._\-]+[A-Z0-9]/;
const bool = /TRUE|FALSE/;
const date = /[0-9]{4,}[\-\/][0-9]+[\-\/][0-9]+/;
const number = /-?(?:[0-9]+|[0-9][0-9,]+[0-9])(?:\.[0-9]*)?/;
const txn = /[*!&#?%PSTCURM]|txn/;
const undatedDirectives = /pushtag|poptag|pushmeta|popmeta|option|plugin|include/;
const directives = /balance|open|close|commodity|pad|event|custom|price|note|document/;
const link = /\^[A-Za-z0-9\-_\/.]+/;
const meta = /[a-z][a-za-z0-9\-_]+:/;

export const beancountStreamParser: StreamParser<unknown> = {
  token(stream) {
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
    if (
      (sol && stream.match(undatedDirectives)) ||
      stream.match(directives) ||
      stream.match(txn)
    ) {
      if (stream.peek() === ":") {
        return "propertyName";
      }
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
    if (stream.match(commodity)) {
      return "unit";
    }
    if (stream.match(string)) {
      if (stream.start === 7 && stream.string.startsWith("option ")) {
        // Option name
        return "string.special";
      }
      return "string";
    }
    if (stream.match(accountRegex)) {
      return "className";
    }
    if (stream.match(meta)) {
      return "propertyName";
    }

    // Skip one character since no known token matched.
    const char = stream.next();
    if (char === "@") {
      return "operator";
    }
    if (char === "{" || char === "}") {
      return "bracket";
    }
    return null;
  },
  languageData: {
    commentTokens: { line: ";" },
  },
};
