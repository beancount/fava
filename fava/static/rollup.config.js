import buble from 'rollup-plugin-buble';
import commonjs from 'rollup-plugin-commonjs';
import json from 'rollup-plugin-json';
import nodeResolve from 'rollup-plugin-node-resolve';
import postcss from 'rollup-plugin-postcss';

import postcssCopy from 'postcss-copy';
import postcssImport from 'postcss-import';
import postcssColorFunction from 'postcss-color-function';
import postcssCustomProperties from 'postcss-custom-properties';
import postcssNesting from 'postcss-nesting';

export default {
  input: 'javascript/main.js',
  output: {
    file: 'gen/app.js',
    format: 'iife',
  },
  moduleContext: {
    'node_modules/whatwg-fetch/fetch.js': 'window',
  },
  plugins: [
    nodeResolve(),
    json(),
    buble({ exclude: 'css/**' }),
    postcss({
      plugins: [
        postcssImport(),
        postcssCopy({
          src: ['css', 'node_modules'],
          dest: 'gen',
        }),
        postcssCustomProperties(),
        postcssColorFunction(),
        postcssNesting(),
      ],
      extract: true,
    }),
    commonjs({
      include: 'node_modules/**',
    }),
  ],
};
