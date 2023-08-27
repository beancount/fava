import { get } from "../../api";
import { todayAsString } from "../../format";
import { _ } from "../../i18n";
import { Route } from "../route";

import ImportSvelte from "./Import.svelte";

/**
 * Construct the filename from date and basename.
 */
function newFilename(date: string | null, basename: string | null): string {
  if (!date || !basename) {
    return "";
  }
  if (/^\d{4}-\d{2}-\d{2}/.test(basename)) {
    return basename;
  }
  return `${date} ${basename}`;
}

interface FileWithImporters<T> {
  name: string;
  basename: string;
  importers: ({ account: string; importer_name: string } & T)[];
}

export type ImportableFile = FileWithImporters<{
  date: string | null;
  name: string | null;
}>;
export type ProcessedImportableFile = FileWithImporters<{ newName: string }>;

/**
 * Initially set the file names for all importable files.
 */
export function preprocessData(
  arr: ImportableFile[],
): ProcessedImportableFile[] {
  const today = todayAsString();
  return arr.map((file) => {
    const importers = file.importers.map(
      ({ account, importer_name, date, name }) => ({
        account,
        importer_name,
        newName: newFilename(date, name),
      }),
    );
    if (importers.length === 0) {
      const newName = newFilename(today, file.basename);
      importers.push({ account: "", newName, importer_name: "" });
    }
    return { ...file, importers };
  });
}

export const import_report = new Route(
  "import",
  ImportSvelte,
  () =>
    get("imports", undefined)
      .then(preprocessData)
      .then((data) => ({ data })),
  () => _("Import"),
);
