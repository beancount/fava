import commonjs from "@rollup/plugin-commonjs";
import nodeResolve from "@rollup/plugin-node-resolve";
import sucrase from "@rollup/plugin-sucrase";
import svelte from "rollup-plugin-svelte";
import typescript from "@rollup/plugin-typescript";

import copy from "./rollup-plugin-copy";
import css from "./rollup-plugin-css";

// Run in dev mode when using rollup watch.
const dev = process.env.ROLLUP_WATCH;

const fonts = [
  "img/favicon.ico",
  "node_modules/@openfonts/fira-mono_all/files/fira-mono-all-400.woff2",
  "node_modules/@openfonts/fira-mono_all/files/fira-mono-all-500.woff2",
  "node_modules/@openfonts/fira-sans_all/files/fira-sans-all-400.woff2",
  "node_modules/@openfonts/fira-sans_all/files/fira-sans-all-500.woff2",
  "node_modules/@openfonts/source-code-pro_all/files/source-code-pro-all-400.woff2",
  "node_modules/@openfonts/source-code-pro_all/files/source-code-pro-all-500.woff2",
  "node_modules/@openfonts/source-serif-pro_latin/files/source-serif-pro-latin-400.woff2",
  "node_modules/@openfonts/source-serif-pro_latin/files/source-serif-pro-latin-600.woff2",
];

const typescriptPlugin = dev
  ? sucrase({
      exclude: ["node_modules/**"],
      transforms: ["typescript"],
    })
  : typescript();

function config(input, outputOpts, ...plugins) {
  return {
    input,
    output: {
      sourcemap: dev,
      format: "iife",
      assetFileNames: "[name]-[hash].[ext]",
      entryFileNames: "[name]-[hash].js",
      ...outputOpts,
    },
    plugins: [
      nodeResolve({ extensions: [".js", ".ts"] }),
      commonjs({
        include: "node_modules/**",
      }),
      svelte({ dev }),
      css(),
      typescriptPlugin,
      sucrase({ exclude: ["node_modules/**"], transforms: [] }),
      copy(fonts),
      ...plugins,
    ],
    onwarn(warning, warn) {
      if (
        warning.code === "CIRCULAR_DEPENDENCY" &&
        warning.importer.includes("d3-")
      ) {
        return;
      }
      warn(warning);
    },
  };
}

export default [config("src/main.ts", { file: "../src/fava/static/app.js" })];
