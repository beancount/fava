import CodeMirror, { Editor, Position } from "codemirror";

CodeMirror.registerHelper(
  "fold",
  "beancount",
  (cm: Editor, start: Position) => {
    const maxDepth = 100;

    function headerLevel(lineNo: number): number {
      const line = cm.getDoc().getLine(lineNo);
      const match = line && /^\*+/.exec(line);
      if (match) {
        return match[0].length;
      }
      return maxDepth;
    }

    const level = headerLevel(start.line);

    if (level === maxDepth) {
      return undefined;
    }

    const doc = cm.getDoc();
    const lastLineNo = doc.lastLine();
    let end = start.line;

    while (end < lastLineNo) {
      if (headerLevel(end + 1) <= level) {
        break;
      }
      end += 1;
    }

    return {
      from: new CodeMirror.Pos(start.line, doc.getLine(start.line).length),
      to: new CodeMirror.Pos(end, doc.getLine(end).length),
    };
  }
);
