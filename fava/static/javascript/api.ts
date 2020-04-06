import { fetchAPI } from "./helpers";
import { notify } from "./notifications";
import { string } from "./lib/validation";

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
    notify(string(msg));
    return true;
  } catch (error) {
    notify(error, "error");
    return false;
  }
}
