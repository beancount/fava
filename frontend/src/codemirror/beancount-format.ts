import type { Command } from "@codemirror/view";

import { put_format_source } from "../api/index.ts";
import { notify_err } from "../notifications.ts";
import { replaceContents } from "./editor-transactions.ts";

export const beancountFormat: Command = (cm) => {
  put_format_source({ source: cm.state.sliceDoc() }).then(
    (data) => {
      cm.dispatch(replaceContents(cm.state, data));
    },
    (error: unknown) => {
      notify_err(error, (err) => `Formatting source failed: ${err.message}`);
    },
  );
  return true;
};
