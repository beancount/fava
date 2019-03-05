import commonjs from "rollup-plugin-commonjs";
import css from "rollup-plugin-css-only";
import json from "rollup-plugin-json";
import svelte from "rollup-plugin-svelte";
import nodeResolve from "rollup-plugin-node-resolve";

import fs from "fs";
import { promisify } from "util";
import { basename, dirname, join } from "path";

const copyFile = promisify(fs.copyFile);

const fonts = [
  "node_modules/typeface-fira-mono/files/fira-mono-latin-400.woff2",
  "node_modules/typeface-fira-mono/files/fira-mono-latin-500.woff2",
  "node_modules/typeface-fira-sans/files/fira-sans-latin-400.woff2",
  "node_modules/typeface-fira-sans/files/fira-sans-latin-500.woff2",
  "node_modules/typeface-source-code-pro/files/source-code-pro-latin-400.woff2",
  "node_modules/typeface-source-code-pro/files/source-code-pro-latin-500.woff2",
  "node_modules/typeface-source-serif-pro/files/source-serif-pro-400.woff2",
  "node_modules/typeface-source-serif-pro/files/source-serif-pro-600.woff2",
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
  input: "javascript/main.js",
  output: {
    file: "gen/app.js",
    format: "iife",
  },
  plugins: [
    nodeResolve(),
    commonjs({
      include: "node_modules/**",
    }),
    svelte(),
    json(),
    css(),
    copy(fonts),
  ],
  onwarn(warning, warn) {
    if (warning.code === "CIRCULAR_DEPENDENCY") return;
    warn(warning);
  },
};
