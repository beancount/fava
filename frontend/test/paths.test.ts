import { equal } from "node:assert/strict";
import { test } from "node:test";

import { basename, documentHasAccount, ext } from "../src/lib/paths.ts";

test("get basename of file", () => {
  equal(basename("/home/Assets/Cash/document.pdf"), "document.pdf");
  equal(basename("/home/Assets/Cash/document ä.pdf"), "document ä.pdf");
  equal(basename("C:\\Assets\\Cash\\document.pdf"), "document.pdf");
  equal(basename("C:\\Assets\\document asdf.pdf"), "document asdf.pdf");
});

test("get file extension", () => {
  equal(ext("/home/Assets/Cash/document.pdf"), "pdf");
  equal(ext("/home/Assets/Cash/document.test.asdf.pdf"), "pdf");
  equal(ext("/home/Assets/Cash/document.test.asdf.c1a"), "c1a");
  equal(ext("/home/Assets/Ca.sh/document"), "");
  equal(ext("/home/Assets/Cash/document ä.pdf"), "pdf");
  equal(ext("C:\\Assets\\Cash\\document.pdf"), "pdf");
  equal(ext("C:\\Assets\\document asdf.pdf"), "pdf");
});

test("detect account of document", () => {
  equal(
    true,
    documentHasAccount("/home/Assets/Cash/document.pdf", "Assets:Cash"),
  );
  equal(
    false,
    documentHasAccount("/home/Assets/Test/Cash/document.pdf", "Assets:Cash"),
  );
  equal(
    true,
    documentHasAccount("C:\\Assets\\Cash\\document.pdf", "Assets:Cash"),
  );
  equal(
    false,
    documentHasAccount("C:\\Assets\\Test\\Cash\\document.pdf", "Assets:Cash"),
  );
});
