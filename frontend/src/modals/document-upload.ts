/**
 * We can handle either files or an URL being dragged-and-dropped.
 */
export function is_supported_datatransfer(
  dataTransfer: DataTransfer | null,
): dataTransfer is DataTransfer {
  return (
    dataTransfer != null &&
    (dataTransfer.types.includes("Files") ||
      (dataTransfer.types.includes("text/uri-list") &&
        new URL(dataTransfer.getData("URL")).searchParams.has("filename")))
  );
}
