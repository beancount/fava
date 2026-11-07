import { readdir, readFile, unlink, writeFile } from "node:fs/promises";
import { basename, dirname, join, resolve } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { type BuildResult, context, type Plugin } from "esbuild";
import svelte from "esbuild-svelte";
import { Features, transform as transform_css } from "lightningcss-wasm";

import package_lock from "./package-lock.json" with { type: "json" };
import { object, string } from "./src/lib/validation.ts";

const filename = fileURLToPath(import.meta.url);
const outdir = join(dirname(filename), "..", "src", "fava", "static");
const entryPoints = [join(dirname(filename), "src", "app.ts")];
const sbom_file = join(dirname(filename), "fava-frontend.cdx.json");

// Minimum supported browsers. Chrome and Safari are pinned by the ES2023
// change-array-by-copy methods (`toSorted` and friends), Firefox by the
// `:has()` CSS selectors.
const target = ["chrome110", "safari16.4", "firefox121"];

/**
 * Lower the `light-dark()` colour values in style.css.
 *
 * Adds support for Safari < 17.5 (relevant for iOS users stuck on devices only
 * receiving security fixes) and Chrome < 123. All other lowering is left to esbuild.
 */
const lightningcss_plugin: Plugin = {
  name: "lightningcss",
  setup(build) {
    build.onLoad({ filter: /\.css$/ }, async ({ path }) => {
      const { code, warnings } = transform_css({
        filename: path,
        code: await readFile(path),
        include: Features.LightDark,
      });
      return {
        contents: new Uint8Array(code),
        loader: "css",
        resolveDir: dirname(path),
        warnings: warnings.map((warning) => ({ text: warning.message })),
      };
    });
  },
};

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

const package_validator = object({ version: string, license: string });

/**
 * Write a CycloneDX SBOM listing the npm packages included in the bundle.
 *
 * This is added to the wheel (in `.dist-info/sboms/`, see PEP 770).
 */
async function write_sbom(result: BuildResult<{ metafile: true }>) {
  const package_dirs = new Set(
    Object.keys(result.metafile.inputs)
      .map((input) => /^node_modules\/(@[^/]+\/)?[^/]+/.exec(input)?.[0])
      .filter((dir) => dir != null),
  );
  const packages: Record<string, unknown> = package_lock.packages;
  const components = [...package_dirs].sort().map((dir) => {
    const res = package_validator(packages[dir]);
    if (!res.is_ok) {
      throw new Error(
        `Invalid package-lock.json entry ${dir}: ${res.error.message}`,
      );
    }
    const name = dir.slice("node_modules/".length);
    const { version, license } = res.value;
    const purl = `pkg:npm/${name.replaceAll("@", "%40")}@${version}`;
    return {
      type: "library",
      "bom-ref": purl,
      name,
      version,
      purl,
      licenses: [{ expression: license }],
    };
  });
  const sbom = {
    $schema: "http://cyclonedx.org/schema/bom-1.6.schema.json",
    bomFormat: "CycloneDX",
    specVersion: "1.6",
    version: 1,
    components,
  };
  const contents = `${JSON.stringify(sbom, null, 2)}\n`;
  const current = await readFile(sbom_file, "utf8").catch(() => null);
  if (contents !== current) {
    await writeFile(sbom_file, contents);
  }
}

/**
 * Build the frontend using esbuild.
 * @param dev - Whether to generate sourcemaps and watch for changes.
 */
async function run_build(dev: boolean) {
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
      lightningcss_plugin,
      svelte({
        compilerOptions: { dev, runes: true },
      }),
    ],
    sourcemap: true,
    target,
  });
  console.log(`starting build, dev=${dev.toString()}`);
  try {
    const result = await ctx.rebuild();
    await cleanup_outdir(result);
    await write_sbom(result);
    console.log("finished build");
  } catch (err: unknown) {
    console.error("build failed", err);
  } finally {
    await ctx.dispose();
  }
}

const is_main = resolve(process.argv[1] ?? "") === filename;

if (is_main) {
  const dev = process.argv.includes("--dev");

  run_build(dev).catch((e: unknown) => {
    console.error(e);
  });
}
