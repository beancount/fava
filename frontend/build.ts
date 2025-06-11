import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import chokidar from "chokidar";
import { context } from "esbuild";
import svelte from "esbuild-svelte";

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
    conditions: dev ? ["development"] : ["production"],
    external: ["fs/promises", "module"], // for web-tree-sitter
    loader: {
      ".wasm": "file",
      ".woff": "empty",
      ".woff2": "file",
    },
    plugins: [
      svelte({
        compilerOptions: { dev, runes: true },
      }),
    ],
    sourcemap: dev,
    target: "esnext",
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
        (err: unknown) => {
          console.error(err);
        },
      );
    }, 200);
    chokidar
      .watch(["src", "css"], {
        awaitWriteFinish: true,
        ignoreInitial: true,
      })
      .on("all", (eventName: string, path: string) => {
        console.log(`${path} ${eventName}`);
        rebuild();
      });
  }
}

const filename = fileURLToPath(import.meta.url);
const is_main = resolve(process.argv[1] ?? "") === filename;

if (is_main) {
  const dev = process.argv.includes("--watch");
  runBuild(dev).catch((e: unknown) => {
    console.error(e);
  });
}
