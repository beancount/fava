import type { Command } from "@codemirror/view";

import { put } from "../api";
import { notify_err } from "../notifications";
import { replaceContents } from "./editor-transactions";

export const beancountFormat: Command = (cm) => {
  put("format_source", { source: cm.state.sliceDoc() }).then(
    (data) => {
      cm.dispatch(replaceContents(cm.state, data));
    },
    (error: unknown) => {
      notify_err(error, (err) => `Formatting source failed: ${err.message}`);
    },
  );
  return true;
};
