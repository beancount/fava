import { Entry } from "../entries";
import { todayAsString } from "../format";

/**
 * Check whether the given entry is marked as duplicate.
 */
export function isDuplicate(e: Entry): boolean {
  return !!e.meta.__duplicate__;
}

/**
 * Construct the filename from date and basename.
 */
function newFilename(date: string, basename: string): string {
  if (/^\d{4}-\d{2}-\d{2}/.test(basename)) {
    return basename;
  }
  if (!date || !basename) {
    return "";
  }
  return `${date} ${basename}`;
}

interface ImporterInfo {
  account: string;
  date: string;
  name: string;
  importer_name: string;
}
interface ImporterInfoWithNewName {
  account: string;
  newName: string;
  importer_name: string;
}

export type ImportableFile<T> = {
  name: string;
  basename: string;
  importers: T[];
};

export type ImportableFiles = ImportableFile<ImporterInfo>[];
export type ProcessedImportableFiles = ImportableFile<ImporterInfoWithNewName>[];

/**
 * Initially set the file names for all importable files.
 */
export function preprocessData(arr: ImportableFiles): ProcessedImportableFiles {
  const today = todayAsString();
  return arr.map((file) => {
    const importers = file.importers.map(
      ({ account, importer_name, date, name }) => ({
        account,
        importer_name,
        newName: newFilename(date, name),
      })
    );
    if (importers.length === 0) {
      const newName = newFilename(today, file.basename);
      importers.push({ account: "", newName, importer_name: "" });
    }
    return { ...file, importers };
  });
}
