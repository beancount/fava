import { get } from "../../api";
import { todayAsString } from "../../format";
import { _ } from "../../i18n";
import { Route } from "../route";
import ImportSvelte from "./Import.svelte";

/**
 * Construct the filename from date and basename.
 *
 * If it already starts with a date use it, otherwise prepend the date
 */
function newFilename(date: string, basename: string): string {
  return /^\d{4}-\d{2}-\d{2}/.test(basename) ? basename : `${date} ${basename}`;
}

export interface ProcessedImportableFile {
  /** Full filename of this file. */
  readonly name: string;
  /** Basename of this file. */
  readonly basename: string;
  /** Whether at least one importer identified this file. */
  readonly identified_by_importers: boolean;
  readonly importers: {
    readonly account: string;
    readonly importer_name: string;
    readonly newName: string;
  }[];
}

export interface ImportReportProps {
  files: ProcessedImportableFile[];
}

export const import_report = new Route<ImportReportProps>(
  "import",
  ImportSvelte,
  async () =>
    get("imports", undefined)
      .then((files) => {
        // Initially set the file names for all importable files.
        const today = todayAsString();
        return files.map((file) => {
          const importers = file.importers.map(
            ({ account, importer_name, date, name }) => ({
              account,
              importer_name,
              newName: newFilename(date, name),
            }),
          );
          const identified_by_importers = importers.length > 0;
          if (!identified_by_importers) {
            const newName = newFilename(today, file.basename);
            importers.push({ account: "", newName, importer_name: "" });
          }
          return { ...file, identified_by_importers, importers };
        });
      })
      .then((files) => ({ files })),
  () => _("Import"),
);
