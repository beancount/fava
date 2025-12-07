import { get_source } from "../../api/index.ts";
import type { SourceFile } from "../../api/validators.ts";
import type { CodemirrorBeancount } from "../../codemirror/types.ts";
import { _ } from "../../i18n.ts";
import { Route } from "../route.ts";
import Editor from "./Editor.svelte";

export interface EditorReportProps {
  source: SourceFile;
  line_search_param: number | null;
  codemirror_beancount: CodemirrorBeancount;
}

export const editor = new Route<EditorReportProps>(
  "editor",
  Editor,
  async (url: URL) => {
    const line = url.searchParams.get("line");
    const line_search_param = line != null ? Number.parseInt(line, 10) : null;
    const [source, codemirror_beancount] = await Promise.all([
      get_source({
        filename: url.searchParams.get("file_path") ?? "",
      }),
      import("../../codemirror/beancount.ts"),
    ]);
    return {
      source,
      line_search_param,
      init_beancount_editor: codemirror_beancount.init_beancount_editor,
      codemirror_beancount,
    };
  },
  () => _("Editor"),
);
