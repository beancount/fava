import { get } from "../../api";
import { getBeancountLanguageSupport } from "../../codemirror/beancount";

export const load = (url: URL) =>
  Promise.all([
    get("source", {
      filename: url.searchParams.get("file_path") ?? "",
    }),
    getBeancountLanguageSupport(),
  ]).then(([source, beancount_language_support]) => ({
    source,
    beancount_language_support,
  }));

export type PageData = Awaited<ReturnType<typeof load>>;
