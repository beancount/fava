/* eslint-disable import/no-extraneous-dependencies */
/* eslint-disable no-console */

/**
 * A script to sync the exact linter dependencies
 * from `./package-lock.json` to `../.pre-commit-config.yaml`
 */

import { ok } from "assert";
import { readFile, writeFile } from "fs/promises";
import { join } from "path";

import { load } from "js-yaml";

import { dependencies } from "./package-lock.json";
import { array, object, optional, string } from "./src/lib/validation";

const preCommitConfigPath = join(__dirname, "..", ".pre-commit-config.yaml");

const confValidator = object({
  repos: array(
    object({
      hooks: array(
        object({
          language: optional(string),
          additional_dependencies: optional(array(string)),
        })
      ),
    })
  ),
});

async function main() {
  const rawConfig = await readFile(preCommitConfigPath, "utf-8");
  let newConfig = rawConfig;
  const conf = confValidator(load(rawConfig));
  ok(conf.success);
  for (const { hooks } of conf.value.repos) {
    for (const { language, additional_dependencies } of hooks) {
      if (language === "node" && additional_dependencies) {
        for (const dep of additional_dependencies) {
          const name = dep.split(/@[^@]*$/)[0] ?? "ERROR";
          const { version } = dependencies[name as keyof typeof dependencies];
          const currentDep = `${name}@${version}`;
          if (dep !== currentDep) {
            console.log(
              `Updating dependency '${name}' from '${dep}' to '${currentDep}'.`
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

main().catch(console.error);
