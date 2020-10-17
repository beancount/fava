import test from "ava";

import { basename, documentHasAccount } from "../src/lib/paths";

test("get basename of file", (t) => {
  t.is(basename("/home/Assets/Cash/document.pdf"), "document.pdf");
  t.is(basename("/home/Assets/Cash/document ä.pdf"), "document ä.pdf");
  t.is(basename("C:\\Assets\\Cash\\document.pdf"), "document.pdf");
  t.is(basename("C:\\Assets\\document asdf.pdf"), "document asdf.pdf");
});

test("detect account of document", (t) => {
  t.true(documentHasAccount("/home/Assets/Cash/document.pdf", "Assets:Cash"));
  t.false(
    documentHasAccount("/home/Assets/Test/Cash/document.pdf", "Assets:Cash")
  );
  t.true(documentHasAccount("C:\\Assets\\Cash\\document.pdf", "Assets:Cash"));
  t.false(
    documentHasAccount("C:\\Assets\\Test\\Cash\\document.pdf", "Assets:Cash")
  );
});
