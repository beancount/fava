import commonjs from "@rollup/plugin-commonjs";
import css from "rollup-plugin-css-only";
import nodeResolve from "@rollup/plugin-node-resolve";
import svelte from "rollup-plugin-svelte";
import typescript from "@rollup/plugin-typescript";

import fs from "fs";
import { promisify } from "util";
import { basename, dirname, join } from "path";

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

export default {
  input: "javascript/main.ts",
  output: {
    file: "gen/app.js",
    name: "fava",
    sourcemap: true,
    format: "iife",
  },
  plugins: [
    nodeResolve(),
    typescript(),
    commonjs({
      include: "node_modules/**",
    }),
    svelte(),
    css(),
    copy(fonts),
  ],
  onwarn(warning, warn) {
    if (warning.code === "CIRCULAR_DEPENDENCY") {
      return;
    }
    warn(warning);
  },
};
