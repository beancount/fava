/* eslint-disable import/no-extraneous-dependencies */
/* eslint-disable no-console */

import chokidar from "chokidar";
import { build } from "esbuild";
import svelte from "esbuild-svelte";
import { typescript } from "svelte-preprocess-esbuild";

/**
 * Create a debounced function.
 */
function debounce(func: () => void, wait: number): () => void {
  let timeout: NodeJS.Timeout | null = null;
  return () => {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => {
      timeout = null;
      func();
    }, wait);
  };
}

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
    // eslint-disable-next-line
    plugins: [svelte({ preprocess: typescript() })],
    sourcemap: dev,
    incremental: dev,
  });
  console.log("finished build");

  if (dev && builder.rebuild) {
    const reb = builder.rebuild;
    console.log("watching for file changes");
    const rebuild = debounce(() => {
      console.log("starting rebuild");
      reb().then(
        () => {
          console.log("finished rebuild");
        },
        (err) => {
          console.error(err);
        }
      );
    }, 200);
    chokidar
      .watch(["src", "css"], {
        awaitWriteFinish: true,
        ignoreInitial: true,
      })
      .on("all", (eventName, path) => {
        console.log(`${path} ${eventName}`);
        rebuild();
      });
  }
}

if (require.main === module) {
  const dev = process.argv.includes("--watch");
  runBuild(dev).catch(console.error);
}
