import { Command } from "@codemirror/view";

import { put } from "../api";
import { notify } from "../notifications";

export const beancountFormat: Command = (cm) => {
  put("format_source", { source: cm.state.doc.toString() }).then(
    (data) => {
      cm.dispatch({
        changes: { from: 0, to: cm.state.doc.length, insert: data },
      });
    },
    (error) => {
      notify(error, "error");
    }
  );
  return true;
};
