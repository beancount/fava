import { fetchAPI } from "./helpers";
import { notify } from "./notifications";

/**
 * Move a file, either in an import directory or a document.
 * @returns whether the file was moved successfully.
 */
export async function moveDocument(
  filename: string,
  account: string,
  newName: string
): Promise<boolean> {
  try {
    const msg = await fetchAPI("move", {
      filename,
      account,
      newName,
    });
    notify(msg as string);
    return true;
  } catch (error) {
    notify(error, "error");
    return false;
  }
}
