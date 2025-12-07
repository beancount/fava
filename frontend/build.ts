import { readdir, unlink } from "node:fs/promises";
import { basename, dirname, join, resolve } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import chokidar from "chokidar";
import { type BuildResult, context } from "esbuild";
import svelte from "esbuild-svelte";
import { sveltePreprocess } from "svelte-preprocess";

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
const outdir = join(dirname(filename), "..", "src", "fava", "static");
const entryPoints = [join(dirname(filename), "src", "app.ts")];

async function cleanup_outdir(result: BuildResult<{ metafile: true }>) {
  // Clean all files in outdir except the ones from this build and favicon.ico
  const to_keep = new Set(
    Object.keys(result.metafile.outputs).map((p) => basename(p)),
  );
  to_keep.add("favicon.ico");
  const outdir_files = await readdir(outdir);
  for (const to_delete of outdir_files.filter((f) => !to_keep.has(f))) {
    console.log(`Cleaning up '${to_delete}'`);
    await unlink(join(outdir, to_delete));
  }
}

/**
 * Build the frontend using esbuild.
 * @param dev - Whether to generate sourcemaps and watch for changes.
 */
async function run_build(dev: boolean, watch: boolean) {
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
        // Needed until sourcemaps in svelte are fixed, see e.g.
        // https://github.com/sveltejs/svelte/issues/17003
        preprocess: sveltePreprocess(),
      }),
    ],
    sourcemap: true,
    target: "esnext",
  });
  console.log(
    `starting build, dev=${dev.toString()}, watch=${watch.toString()}`,
  );
  const result = await ctx.rebuild();
  await cleanup_outdir(result);
  console.log("finished build");

  if (!watch) {
    await ctx.dispose();
  } else {
    console.log("watching for file changes");
    const rebuild = debounce(() => {
      console.log("starting rebuild");
      ctx
        .rebuild()
        .then(async (result) => cleanup_outdir(result))
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

const is_main = resolve(process.argv[1] ?? "") === filename;

if (is_main) {
  const watch = process.argv.includes("--watch");
  const dev = process.argv.includes("--dev");

  run_build(dev, watch).catch((e: unknown) => {
    console.error(e);
  });
}
