const CodeMirror = require('codemirror/lib/codemirror');

// The rules should mirror `parser/lexel.l` in beancount
CodeMirror.defineSimpleMode('beancount', {
  start: [
    {
      regex: /\*.*/,
      token: 'comment section',
      sol: true,
    },
    {
      regex: /[#*;].*/,
      token: 'comment',
      sol: true,
    },
    {
      regex: /;.*/,
      token: 'comment',
    },
    {
      regex: /(query)(\s*)("[^"]*")(\s*)(")/,
      token: ['directive', null, 'string', null, 'string'],
      mode: {
        spec: 'text/x-sql',
        end: /"/,
      },
    },
    {
      regex: /"(?:[^\\]|\\.)*?"/,
      token: 'string',
    },
    {
      regex: /@|@@|{|}/,
      token: 'bracket',
    },
    {
      regex: /\s+/,
      token: 'whitespace',
    },
    {
      regex: /[*!&#?%PSTCURM]|txn/,
      token: 'directive transaction',
    },
    // other dated directives
    {
      regex: /balance|open|close|commodity|pad|event|custom|price|note|document/,
      token: 'directive',
    },
    // undated directives
    {
      regex: /pushtag|poptag|pushmeta|popmeta|option|plugin|include/,
      token: 'directive',
      sol: true,
    },
    {
      regex: /TRUE|FALSE/,
      token: 'bool atom',
    },
    {
      regex: /[0-9]{4,}[\-\/][0-9]+[\-\/][0-9]+/,
      token: 'date',
    },
    {
      regex: /(?:[A-Z][A-Za-z0-9\-]+)(?::[A-Z][A-Za-z0-9\-]+)+/,
      token: 'account',
    },
    {
      regex: /[A-Z][A-Z0-9'\._\-]{0,22}[A-Z0-9]/,
      token: 'commodity keyword',
    },
    {
      regex: /(?:[0-9]+|[0-9][0-9,]+[0-9])(?:\.[0-9]*)?/,
      token: 'number',
    },
    {
      regex: /#[A-Za-z0-9\-_\/.]+/,
      token: 'tag',
    },
    {
      regex: /\^[A-Za-z0-9\-_\/.]+/,
      token: 'attribute',
    },
    {
      regex: /[a-z][a-za-z0-9\-_]+:/,
      token: 'meta',
    },
  ],
});
