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
    if (stream.eatSpace() || stream.eol()) {
      return null;
    }
    const sol = stream.sol();
    if (sol && (stream.match(sectionComment) || stream.match(comment))) {
      return "lineComment";
    }
    if (
      (sol && stream.match(undatedDirectives)) ||
      stream.match(directives) ||
      stream.match(txn)
    ) {
      if (stream.peek() === ":") {
        return "labelName";
      }
      return "keyword";
    }
    if (stream.match(inlineComment)) {
      return "comment";
    }
    if (stream.match(date) || stream.match(number)) {
      return "number";
    }
    if (stream.match(bool)) {
      return "bool";
    }
    if (stream.match(commodity)) {
      return "keyword";
    }
    if (stream.match(string)) {
      return "string";
    }
    if (stream.match(accountRegex)) {
      return "className";
    }
    if (stream.match(tag) || stream.match(link)) {
      return "propertyName";
    }
    if (stream.match(meta)) {
      return "labelName";
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
