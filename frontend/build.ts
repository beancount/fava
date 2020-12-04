/* eslint-disable import/no-extraneous-dependencies */
/* eslint-disable no-console */

import chokidar from "chokidar";
import { build } from "esbuild";
import svelte from "esbuild-plugin-svelte";

/**
 * Build the frontend using esbuild.
 * @param dev - Whether to generate sourcemaps and watch for changes.
 */
async function runBuild(dev: boolean) {
  console.log("starting build");
  const builder = await build({
    entryPoints: ["src/main.ts"],
    bundle: true,
    outfile: "../src/fava/static/app.js",
    loader: {
      ".woff2": "file",
    },
    plugins: [svelte()],
    sourcemap: dev,
    incremental: dev,
  });
  console.log("finished build");

  if (dev) {
    console.log("watching for file changes");
    chokidar
      .watch("src/**/*.{ts,svelte}", {
        awaitWriteFinish: true,
        ignoreInitial: true,
      })
      .on("all", async (eventName, path) => {
        console.log(`${path} ${eventName}`);
        if (builder.rebuild) {
          await builder.rebuild();
          console.log("finished build");
        }
      });
  }
}

if (require.main === module) {
  const dev = process.argv.includes("--watch");
  runBuild(dev);
}
