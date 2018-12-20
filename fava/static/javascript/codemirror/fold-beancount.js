import CodeMirror from "codemirror";

CodeMirror.registerHelper("fold", "beancount", (cm, start) => {
  const maxDepth = 100;

  function headerLevel(lineNo) {
    const line = cm.getLine(lineNo);
    const match = line && line.match(/^\*+/);
    if (match) {
      return match[0].length;
    }
    return maxDepth;
  }

  const level = headerLevel(start.line);

  if (level === maxDepth) {
    return undefined;
  }

  const lastLineNo = cm.lastLine();
  let end = start.line;

  while (end < lastLineNo) {
    if (headerLevel(end + 1) <= level) {
      break;
    }
    end += 1;
  }

  return {
    from: new CodeMirror.Pos(start.line, cm.getLine(start.line).length),
    to: new CodeMirror.Pos(end, cm.getLine(end).length),
  };
});
