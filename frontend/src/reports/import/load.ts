import { get } from "../../api";
import { todayAsString } from "../../format";

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

interface FileWithImporters<T> {
  name: string;
  basename: string;
  importers: ({ account: string; importer_name: string } & T)[];
}

export type ImportableFile = FileWithImporters<{ date: string; name: string }>;
export type ProcessedImportableFile = FileWithImporters<{ newName: string }>;

/**
 * Initially set the file names for all importable files.
 */
export function preprocessData(
  arr: ImportableFile[]
): ProcessedImportableFile[] {
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

export const load = () => get("imports", undefined).then(preprocessData);

export type PageData = Awaited<ReturnType<typeof load>>;
