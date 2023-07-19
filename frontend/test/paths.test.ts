import { test } from "uvu";
import assert from "uvu/assert";

import { basename, documentHasAccount, ext } from "../src/lib/paths";

test("get basename of file", () => {
  assert.is(basename("/home/Assets/Cash/document.pdf"), "document.pdf");
  assert.is(basename("/home/Assets/Cash/document ä.pdf"), "document ä.pdf");
  assert.is(basename("C:\\Assets\\Cash\\document.pdf"), "document.pdf");
  assert.is(basename("C:\\Assets\\document asdf.pdf"), "document asdf.pdf");
});

test("get file extension", () => {
  assert.is(ext("/home/Assets/Cash/document.pdf"), "pdf");
  assert.is(ext("/home/Assets/Cash/document.test.asdf.pdf"), "pdf");
  assert.is(ext("/home/Assets/Cash/document.test.asdf.c1a"), "c1a");
  assert.is(ext("/home/Assets/Ca.sh/document"), "");
  assert.is(ext("/home/Assets/Cash/document ä.pdf"), "pdf");
  assert.is(ext("C:\\Assets\\Cash\\document.pdf"), "pdf");
  assert.is(ext("C:\\Assets\\document asdf.pdf"), "pdf");
});

test("detect account of document", () => {
  assert.is(
    true,
    documentHasAccount("/home/Assets/Cash/document.pdf", "Assets:Cash"),
  );
  assert.is(
    false,
    documentHasAccount("/home/Assets/Test/Cash/document.pdf", "Assets:Cash"),
  );
  assert.is(
    true,
    documentHasAccount("C:\\Assets\\Cash\\document.pdf", "Assets:Cash"),
  );
  assert.is(
    false,
    documentHasAccount("C:\\Assets\\Test\\Cash\\document.pdf", "Assets:Cash"),
  );
});

test.run();
