/**
 * A script to fetch the latest github actions versions and update them.
 */

import { readdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { object, string } from "./src/lib/validation";

const workflows = join(
  fileURLToPath(import.meta.url),
  "..",
  "..",
  ".github",
  "workflows",
);
const action_regex = /uses: ([-/\w]+)@(\S+)/g;
const release_validator = object({ tag_name: string });

/**
 * Fetches the latest release tag name for a given GitHub repository ('owner/repo').
 */
async function get_latest_release_version(owner_repo: string): Promise<string> {
  const url = `https://api.github.com/repos/${owner_repo}/releases/latest`;
  const response = await fetch(url, {
    headers: {
      Accept: "application/vnd.github+json",
      "User-Agent": "sync-actions-script",
    },
  });

  if (!response.ok) {
    console.error(response);
    throw new Error("Error fetching latest release");
  }
  const data: unknown = await response.json();
  return release_validator(data).unwrap().tag_name;
}

async function main() {
  const workflow_files = (await readdir(workflows)).map((name) =>
    join(workflows, name),
  );
  console.log("Workflow files:");
  console.log(workflow_files);

  const actions = new Map<string, string>();
  for (const path of workflow_files) {
    const contents = await readFile(path, "utf-8");
    for (const match of contents.matchAll(action_regex)) {
      if (match[1] != null && match[2] != null) {
        actions.set(match[1], match[2]);
      }
    }
  }
  console.log("Found the following used actions:");
  console.log(actions);

  for (const [action, current] of actions.entries()) {
    const latest = await get_latest_release_version(action);
    const latest_short = latest.split(".")[0] ?? "";
    console.log(
      `Latest version for '${action}' is: ${latest_short} (${latest})`,
    );

    if (latest_short !== current) {
      console.log(
        `--> updating version for '${action}': from ${current} to ${latest_short}`,
      );

      for (const path of workflow_files) {
        const contents = await readFile(path, "utf-8");
        const updated_contents = contents.replaceAll(
          action_regex,
          (match, matched_action: string, current_version: string) =>
            matched_action === action && current_version !== latest_short
              ? `uses: ${matched_action}@${latest_short}`
              : match,
        );

        if (updated_contents !== contents) {
          await writeFile(path, updated_contents, "utf-8");
        }
      }
    }
  }
}

main().catch((e: unknown) => {
  console.error(e);
});
