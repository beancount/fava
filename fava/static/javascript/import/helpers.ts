/**
 * Construct the filename from date and basename.
 */
export function newFilename(date: string, basename: string): string {
  if (/^\d{4}-\d{2}-\d{2}/.test(basename)) {
    return basename;
  }
  if (!date || !basename) {
    return "";
  }
  return `${date} ${basename}`;
}

/**
 * Generate the URL hash for extracting the extract modal.
 */
export function extractURL(filename: string, importer: string): string {
  const params = new URLSearchParams();
  params.set("filename", filename);
  params.set("importer", importer);
  return `#extract-${params.toString()}`;
}
