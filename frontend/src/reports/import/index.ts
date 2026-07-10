import { get_imports } from "../../api/index.ts";
import { todayAsString } from "../../format.ts";
import { _ } from "../../i18n.ts";
import { Route } from "../route.ts";
import ImportSvelte from "./Import.svelte";

/**
 * Construct the filename from date and basename.
 *
 * If it already starts with a date use it, otherwise prepend the date
 */
function new_filename(date: string, basename: string): string {
  return /^\d{4}-\d{2}-\d{2}/.test(basename) ? basename : `${date} ${basename}`;
}

class FileImporterInfo {
  /** Account that the importer determined. */
  readonly account: string;
  /** Name of the importer (uniquely identifies the importer). */
  readonly importer_name: string | null;
  /** New file basename, as inititally determined by the importer */
  readonly new_name: string;

  constructor(account: string, importer_name: string | null, new_name: string) {
    this.account = account;
    this.importer_name = importer_name;
    this.new_name = new_name;
  }
}

export interface ProcessedImportableFile {
  /** Full filename of this file. */
  readonly name: string;
  /** Basename of this file. */
  readonly basename: string;
  /** Whether at least one importer identified this file. */
  readonly identified_by_importers: boolean;
  readonly importers: FileImporterInfo[];
}

export interface ImportReportProps {
  files: ProcessedImportableFile[];
}

export const import_report = new Route<ImportReportProps>(
  "import",
  ImportSvelte,
  async () =>
    get_imports()
      .then((files) => {
        const today = todayAsString();
        return files.map(({ name, basename, importers }) => ({
          name,
          basename,
          identified_by_importers: importers.length > 0,
          importers:
            importers.length > 0
              ? importers.map(
                  ({ account, importer_name, date, name }) =>
                    new FileImporterInfo(
                      account,
                      importer_name,
                      new_filename(date, name),
                    ),
                )
              : [new FileImporterInfo("", null, new_filename(today, basename))],
        }));
      })
      .then((files) => ({ files })),
  () => _("Import"),
);
