import type { Command } from "@codemirror/view";

import { put_format_source } from "../api/index.ts";
import { notify_err } from "../notifications.ts";
import { replace_contents } from "./editor-transactions.ts";

export const beancount_format: Command = (cm) => {
  put_format_source({ source: cm.state.sliceDoc() }).then(
    (data) => {
      cm.dispatch(replace_contents(cm.state, data));
    },
    (error: unknown) => {
      notify_err(error, (err) => `Formatting source failed: ${err.message}`);
    },
  );
  return true;
};
