/* eslint-disable import/no-extraneous-dependencies */
/* eslint-disable no-console */

import chokidar from "chokidar";
import { context } from "esbuild";
import svelte from "esbuild-svelte";
import { typescript } from "svelte-preprocess-esbuild";

import { compilerOptions } from "./tsconfig.json";

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
  const ctx = await context({
    entryPoints: ["src/main.ts"],
    format: "esm",
    bundle: true,
    outfile: "../src/fava/static/app.js",
    external: ["fs", "path"], // for web-tree-sitter
    loader: {
      ".wasm": "file",
      ".woff": "empty",
      ".woff2": "file",
    },
    plugins: [svelte({ preprocess: typescript() })],
    sourcemap: dev,
    target: compilerOptions.target,
  });
  console.log("starting build");
  await ctx.rebuild();
  console.log("finished build");

  if (!dev) {
    await ctx.dispose();
  } else {
    console.log("watching for file changes");
    const rebuild = debounce(() => {
      console.log("starting rebuild");
      ctx.rebuild().then(
        () => {
          console.log("finished rebuild");
        },
        (err) => {
          console.error(err);
        },
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
