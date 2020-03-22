import commonjs from "@rollup/plugin-commonjs";
import css from "rollup-plugin-css-only";
import nodeResolve from "@rollup/plugin-node-resolve";
import sucrase from "@rollup/plugin-sucrase";
import svelte from "rollup-plugin-svelte";
import typescript from "@rollup/plugin-typescript";

import fs from "fs";
import { promisify } from "util";
import { basename, dirname, join } from "path";

// Run in dev mode when using rollup watch.
const production = !process.env.ROLLUP_WATCH;

const copyFile = promisify(fs.copyFile);

const fonts = [
  "node_modules/@openfonts/fira-mono_all/files/fira-mono-all-400.woff2",
  "node_modules/@openfonts/fira-mono_all/files/fira-mono-all-500.woff2",
  "node_modules/@openfonts/fira-sans_all/files/fira-sans-all-400.woff2",
  "node_modules/@openfonts/fira-sans_all/files/fira-sans-all-500.woff2",
  "node_modules/@openfonts/source-code-pro_all/files/source-code-pro-all-400.woff2",
  "node_modules/@openfonts/source-code-pro_all/files/source-code-pro-all-500.woff2",
  "node_modules/@openfonts/source-serif-pro_latin/files/source-serif-pro-latin-400.woff2",
  "node_modules/@openfonts/source-serif-pro_latin/files/source-serif-pro-latin-600.woff2",
];

/**
 * Copy the fonts over to the bundle folder.
 */
function copy(files) {
  return {
    name: "rollup-plugin-copy",
    generateBundle(options) {
      return Promise.all(
        files.map(file =>
          copyFile(file, join(dirname(options.file), basename(file)))
        )
      );
    },
  };
}

const typescriptPlugin = production
  ? typescript()
  : sucrase({
      exclude: ["node_modules/**"],
      transforms: ["typescript"],
    });

export default {
  input: "javascript/main.ts",
  output: {
    file: "gen/app.js",
    name: "fava",
    sourcemap: true,
    format: "iife",
  },
  plugins: [
    nodeResolve({ extensions: [".js", ".ts"] }),
    commonjs({
      include: "node_modules/**",
    }),
    svelte({ dev: !production }),
    css(),
    typescriptPlugin,
    copy(fonts),
  ],
  onwarn(warning, warn) {
    if (warning.code === "CIRCULAR_DEPENDENCY") {
      return;
    }
    warn(warning);
  },
};
