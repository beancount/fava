import { get } from "../../api";
import { getBeancountLanguageSupport } from "../../codemirror/beancount";
import { _ } from "../../i18n";
import { Route } from "../route";
import Editor from "./Editor.svelte";

export const editor = new Route(
  "editor",
  Editor,
  async (url: URL) =>
    Promise.all([
      get("source", {
        filename: url.searchParams.get("file_path") ?? "",
      }),
      getBeancountLanguageSupport(),
    ]).then(([source, beancount_language_support]) => ({
      source,
      beancount_language_support,
    })),
  () => _("Editor"),
);
