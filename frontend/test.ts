import { resolve } from "node:path";
import process from "node:process";
import { run } from "node:test";
import { spec } from "node:test/reporters";
import { fileURLToPath } from "node:url";

const filename = fileURLToPath(import.meta.url);
const is_main = resolve(process.argv[1] ?? "") === filename;

if (is_main) {
  const watch = process.argv.includes("--watch");

  run({
    globPatterns: ["test/**/*.test.ts"],
    coverage: true,
    coverageIncludeGlobs: ["src/**/*.svelte", "src/**/*.ts"],
    watch,
    // This would spped up the test run but does not work with
    // coverage right now unfortunately:
    // isolation: "none",
  })
    .on("test:fail", () => {
      process.exitCode = 1;
    })
    .compose(spec)
    .pipe(process.stdout);
}
