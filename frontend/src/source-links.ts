import { get as store_get } from "svelte/store";

import { put_open_in_editor } from "./api/index.ts";
import { type SourceLink, sourceLink } from "./helpers.ts";
import { notify_err } from "./notifications.ts";

/** Resolve the source link target for a file and line. */
export function source_link_for(
  file_path: string,
  line: string | number,
): SourceLink {
  return store_get(sourceLink)(file_path, line.toString());
}

/**
 * Execute the external editor command if configured.
 * @returns true if the click was handled (command attempted), false otherwise.
 */
export async function maybe_open_in_external_editor(
  target: SourceLink,
  file_path: string,
  line: string | number,
): Promise<boolean> {
  if (target.mode !== "command") {
    return false;
  }
  try {
    await put_open_in_editor({ file_path, line: String(line) });
  } catch (error) {
    notify_err(error);
  }
  return true;
}
