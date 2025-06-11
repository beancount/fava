/**
 * A script to sync the exact linter dependencies
 * from `./package-lock.json` to `../.pre-commit-config.yaml`
 */

import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import package_lock from "./package-lock.json" with { type: "json" };

const { packages } = package_lock;

const config_path = join(
  fileURLToPath(import.meta.url),
  "..",
  "..",
  ".pre-commit-config.yaml",
);

async function main() {
  const current_config = await readFile(config_path, "utf-8");
  let new_config = current_config;

  for (const [pack, { version }] of Object.entries(packages)) {
    const name = pack.substring("node_modules/".length);
    if (name) {
      new_config = new_config.replaceAll(
        new RegExp(`"${name}@[\\d\\.]+"`, "g"),
        `"${name}@${version}"`,
      );
    }
  }

  if (new_config !== current_config) {
    console.log("Writing updated pre-commit config.");
    await writeFile(config_path, new_config, "utf-8");
  }
}

main().catch((e: unknown) => {
  console.error(e);
});
