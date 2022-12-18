import type { Command } from "@codemirror/view";

import { put } from "../api";
import { notify_err } from "../notifications";

export const beancountFormat: Command = (cm) => {
  put("format_source", { source: cm.state.sliceDoc() }).then(
    (data) => {
      cm.dispatch({
        changes: { from: 0, to: cm.state.doc.length, insert: data },
      });
    },
    (error) => {
      notify_err(error, (err) => `Formatting source failed: ${err.message}`);
    }
  );
  return true;
};
