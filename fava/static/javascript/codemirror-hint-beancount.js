const CodeMirror = require('codemirror/lib/codemirror');
const fuzzy = require('fuzzyjs');

function getCurrentWord(cursor, line) {
  return line.slice(0, cursor.ch).match(/(\S*)$/)[0];
}

function fuzzyMatch(cursor, currentWord, completions) {
  const search = currentWord.toLowerCase();
  return {
    list: fuzzy.filter(search, completions, {}),
    from: new CodeMirror.Pos(cursor.line, cursor.ch - currentWord.length),
    to: cursor,
  };
}

const completionSources = {
  accounts: window.allAccounts,
  commodities: window.allCommodities,
  tags: window.allTags,
  undatedDirectives: ['option', 'plugin', 'include'],
  datedDirectives: ['open', 'close', 'commodity', 'balance', 'pad', 'note', 'document', 'price',
                    'event', 'query'],
};

const directiveCompletions = {
  open: ['accounts', 'commodities'],
  close: ['accounts'],
  commodity: ['commodities'],
  balance: ['accounts', null, 'commodities'],
  pad: ['accounts', 'accounts'],
  note: ['accounts'],
  document: ['accounts'],
  price: ['commodities', null, 'commodities'],
};

CodeMirror.registerHelper('hint', 'beancount', (cm) => {
  const cursor = cm.getCursor();
  const line = cm.getLine(cursor.line);
  const token = cm.getTokenAt(cursor);
  const currentCharacter = line[cursor.ch - 1];
  const currentWord = getCurrentWord(cursor, line);

  // If '#' has just been typed, there won't be a tag token yet
  if (currentCharacter === '#') {
    return {
      list: completionSources.tags,
      from: cursor,
      to: cursor,
    };
  }

  if (token.type === 'tag') {
    return {
      list: completionSources.tags.filter((d) => d.startsWith(currentWord.slice(1))),
      from: new CodeMirror.Pos(cursor.line, token.start + 1),
      to: new CodeMirror.Pos(cursor.line, token.end),
    };
  }

  // directives at the start of the line
  if (currentWord === line && line.length > 0) {
    return {
      list: completionSources.undatedDirectives.filter((d) => d.startsWith(currentWord)),
      from: new CodeMirror.Pos(cursor.line, 0),
      to: cursor,
    };
  }

  const lineTokens = cm.getLineTokens(cursor.line);

  if (lineTokens.length > 0) {
    const startCurrentWord = cursor.ch - currentWord.length;
    const previousTokens = lineTokens.filter((d) => d.end <= startCurrentWord);

    // complete accounts for indented lines
    if (lineTokens[0].type === 'whitespace') {
      if (previousTokens.length === 1) {
        return fuzzyMatch(cursor, currentWord, completionSources.accounts);
      }
    }

    // dated directives
    if (lineTokens[0].type === 'date') {
      // date whitespace -> complete directives
      if (previousTokens.length === 2) {
        return {
          list: completionSources.datedDirectives.filter((d) => d.startsWith(currentWord)),
          from: new CodeMirror.Pos(cursor.line, cursor.ch - currentWord.length),
          to: cursor,
        };
      }

      if (previousTokens.length % 2 === 0) {
        const directiveType = previousTokens[2].string;
        if (directiveType in directiveCompletions) {
          const completionType = directiveCompletions[directiveType][previousTokens.length / 2 - 2];
          return fuzzyMatch(cursor, currentWord, completionSources[completionType]);
        }
      }
    }
  }

  return {
    list: [],
  };
});
