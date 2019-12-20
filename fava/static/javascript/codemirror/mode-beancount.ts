/* eslint-disable no-useless-escape */
// To keep the regular expressions in sync with Beancount, they might contain
// some superfluous escape characters.

import CodeMirror from "codemirror";

// The rules should mirror `parser/lexel.l` in beancount
CodeMirror.defineSimpleMode("beancount", {
  start: [
    {
      regex: /\*.*/,
      token: "comment section",
      sol: true,
    },
    {
      regex: /[#*;].*/,
      token: "comment",
      sol: true,
    },
    {
      regex: /;.*/,
      token: "comment",
    },
    {
      regex: /(query)(\s*)("[^"]*")(\s*)(")/,
      token: ["directive", "", "string", "", "string"],
      mode: {
        spec: "beancount-query",
        end: /"/,
      },
    },
    {
      regex: /"(?:[^\\]|\\.)*?"/,
      token: "string",
    },
    {
      regex: /@|@@|{|}/,
      token: "bracket",
    },
    {
      regex: /\s+/,
      token: "whitespace",
    },
    {
      regex: /#[A-Za-z0-9\-_\/.]+/,
      token: "tag",
    },
    {
      regex: /[A-Z][A-Z0-9'\._\-]{0,22}[A-Z0-9]/,
      token: "commodity keyword",
    },
    {
      regex: /TRUE|FALSE/,
      token: "bool atom",
    },
    {
      regex: /(?:[A-Z][A-Za-z0-9\-]+)(?::[A-Z][A-Za-z0-9\-]*)+/,
      token: "account",
    },
    {
      regex: /[*!&#?%PSTCURM]|txn/,
      token: "directive transaction",
    },
    // other dated directives
    {
      regex: /balance|open|close|commodity|pad|event|custom|price|note|document/,
      token: "directive",
    },
    // undated directives
    {
      regex: /pushtag|poptag|pushmeta|popmeta|option|plugin|include/,
      token: "directive",
      sol: true,
    },
    {
      regex: /[0-9]{4,}[\-\/][0-9]+[\-\/][0-9]+/,
      token: "date",
    },
    {
      regex: /(?:[0-9]+|[0-9][0-9,]+[0-9])(?:\.[0-9]*)?/,
      token: "number",
    },
    {
      regex: /\^[A-Za-z0-9\-_\/.]+/,
      token: "attribute",
    },
    {
      regex: /[a-z][a-za-z0-9\-_]+:/,
      token: "meta",
    },
  ],
});
