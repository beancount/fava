import { foldService } from "@codemirror/language";

const MAXDEPTH = 100;

function headerLevel(line: string): number {
  const match = /^\*+/.exec(line);
  return match?.[0]?.length ?? MAXDEPTH;
}

export const beancountFold = foldService.of(({ doc }, lineStart, lineEnd) => {
  const startLine = doc.lineAt(lineStart);
  const totalLines = doc.lines;
  const level = headerLevel(startLine.text);
  if (level === MAXDEPTH) {
    return null;
  }
  let lineNo = startLine.number;
  let end = startLine.to;
  while (lineNo < totalLines) {
    lineNo += 1;
    const line = doc.line(lineNo);
    if (headerLevel(line.text) <= level) {
      break;
    }
    end = line.to;
  }
  return { from: lineEnd, to: end };
});
