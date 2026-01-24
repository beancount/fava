import { readdir, unlink } from "node:fs/promises";
import { basename, dirname, join, resolve } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import chokidar from "chokidar";
import { type BuildResult, context } from "esbuild";
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

const filename = fileURLToPath(import.meta.url);
const outdir = join(dirname(filename), "..", "src", "rustfava", "static");
const entryPoints = [join(dirname(filename), "src", "app.ts")];

async function cleanupOutdir(result: BuildResult<{ metafile: true }>) {
  // Clean all files in outdir except the ones from this build and favicon.ico
  const toKeep = new Set(
    Object.keys(result.metafile.outputs).map((p) => basename(p)),
  );
  toKeep.add("favicon.ico");
  const outdirFiles = await readdir(outdir);
  for (const toDelete of outdirFiles.filter((f) => !toKeep.has(f))) {
    console.log(`Cleaning up '${toDelete}'`);
    await unlink(join(outdir, toDelete));
  }
}

/**
 * Build the frontend using esbuild.
 * @param dev - Whether to generate sourcemaps and watch for changes.
 */
async function runBuild(dev: boolean, watch: boolean) {
  const ctx = await context({
    entryPoints,
    outdir,
    format: "esm",
    bundle: true,
    splitting: true,
    metafile: true,
    conditions: dev ? ["development"] : ["production"],
    external: ["fs/promises", "module"], // for web-tree-sitter
    resolveExtensions: [], // enforce explicit extensions
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
    sourcemap: true,
    target: "esnext",
  });
  console.log(
    `starting build, dev=${dev.toString()}, watch=${watch.toString()}`,
  );
  const result = await ctx.rebuild();
  await cleanupOutdir(result);
  console.log("finished build");

  if (!watch) {
    await ctx.dispose();
  } else {
    console.log("watching for file changes");
    const rebuild = debounce(() => {
      console.log("starting rebuild");
      ctx
        .rebuild()
        .then(async (result) => cleanupOutdir(result))
        .then(() => {
          console.log("finished rebuild");
        })
        .catch((err: unknown) => {
          console.error(err);
        });
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

const isMain = resolve(process.argv[1] ?? "") === filename;

if (isMain) {
  const watch = process.argv.includes("--watch");
  const dev = process.argv.includes("--dev");

  runBuild(dev, watch).catch((e: unknown) => {
    console.error(e);
  });
}
