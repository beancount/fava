import type { LanguageSupport } from "@codemirror/language";

import { get } from "../../api";
import type { SourceFile } from "../../api/validators";
import { getBeancountLanguageSupport } from "../../codemirror/beancount";
import { _ } from "../../i18n";
import { Route } from "../route";
import Editor from "./Editor.svelte";

export interface EditorReportProps {
  source: SourceFile;
  beancount_language_support: LanguageSupport;
  line_search_param: number | null;
}

export const editor = new Route<EditorReportProps>(
  "editor",
  Editor,
  async (url: URL) => {
    const line = url.searchParams.get("line");
    const line_search_param = line != null ? Number.parseInt(line, 10) : null;
    return Promise.all([
      get("source", {
        filename: url.searchParams.get("file_path") ?? "",
      }),
      getBeancountLanguageSupport(),
    ]).then(([source, beancount_language_support]) => ({
      source,
      beancount_language_support,
      line_search_param,
    }));
  },
  () => _("Editor"),
);
