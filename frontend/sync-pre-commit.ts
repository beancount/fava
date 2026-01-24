/**
 * A script to sync the exact linter dependencies
 * from `./bun.lock` to `../.pre-commit-config.yaml`
 */

import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

interface BunLock {
  packages: Record<string, [string, ...unknown[]]>;
}

const script_dir = join(fileURLToPath(import.meta.url), "..");
const lock_path = join(script_dir, "bun.lock");

const config_path = join(script_dir, "..", ".pre-commit-config.yaml");

async function main() {
  const lock_content = await readFile(lock_path, "utf-8");
  const bun_lock = JSON.parse(lock_content) as BunLock;
  const packages = bun_lock.packages;

  const current_config = await readFile(config_path, "utf-8");
  let new_config = current_config;

  for (const [name, info] of Object.entries(packages)) {
    // info[0] is "package@version"
    const version = info[0].split("@").pop();
    if (name && version) {
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
