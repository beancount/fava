/**
 * A script to sync the exact linter dependencies
 * from `./package-lock.json` to `../.pre-commit-config.yaml`
 */

import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

import { load } from "js-yaml";

import { packages } from "./package-lock.json";
import { array, object, optional, string } from "./src/lib/validation";

const preCommitConfigPath = join(__dirname, "..", ".pre-commit-config.yaml");

const confValidator = object({
  repos: array(
    object({
      hooks: array(
        object({
          language: optional(string),
          additional_dependencies: optional(array(string)),
        }),
      ),
    }),
  ),
});

async function main() {
  const rawConfig = await readFile(preCommitConfigPath, "utf-8");
  let newConfig = rawConfig;
  const conf = confValidator(load(rawConfig));
  for (const { hooks } of conf.unwrap().repos) {
    for (const { language, additional_dependencies } of hooks) {
      if (language === "node" && additional_dependencies) {
        for (const dep of additional_dependencies) {
          const name = dep.split(/@[^@]*$/)[0] ?? "ERROR";
          const { version } =
            packages[`node_modules/${name}` as keyof typeof packages];
          const currentDep = `${name}@${version}`;
          if (dep !== currentDep) {
            console.log(
              `Updating dependency '${name}' from '${dep}' to '${currentDep}'.`,
            );
            newConfig = newConfig.replace(`"${dep}"`, `"${currentDep}"`);
          }
        }
      }
    }
  }
  if (newConfig !== rawConfig) {
    console.log("Writing updated pre-commit config.");
    await writeFile(preCommitConfigPath, newConfig, "utf-8");
  }
}

main().catch((e: unknown) => {
  console.error(e);
});
