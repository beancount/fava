import buble from 'rollup-plugin-buble';
import commonjs from 'rollup-plugin-commonjs';
import json from 'rollup-plugin-json';
import nodeResolve from 'rollup-plugin-node-resolve';
import postcss from 'rollup-plugin-postcss';

import postcssCopy from 'postcss-copy';
import postcssImport from 'postcss-import';
import postcssCssnext from 'postcss-cssnext';

export default {
  entry: 'javascript/main.js',
  dest: 'gen/app.js',
  format: 'iife',
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
        postcssCssnext(),
      ],
      extract: 'gen/style.css',
    }),
    commonjs({
      include: 'node_modules/**',
    }),
  ],
};
