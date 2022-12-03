import { get } from "../../api";

export const load = (url: URL) =>
  get("source", {
    filename: url.searchParams.get("file_path") ?? "",
  });

export type PageData = Awaited<ReturnType<typeof load>>;
