import buble from 'rollup-plugin-buble';
import commonjs from 'rollup-plugin-commonjs';
import json from 'rollup-plugin-json';
import nodeResolve from 'rollup-plugin-node-resolve';
import sass from 'rollup-plugin-sass';

import postcss from 'postcss';
import copy from 'postcss-copy';

const postcssPlugins = [
  copy({
    src: ['sass', 'node_modules'],
    dest: 'gen',
    inputPath() {
      return 'sass';
    },
  }),
];

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
    buble({
      exclude: 'sass/**',
    }),
    sass({
      output: 'gen/style.css',
      options: {
        includePaths: ['node_modules/'],
      },
      processor(style) {
        return postcss(postcssPlugins)
          .process(style)
          .then(result => result);
      },
    }),
    commonjs({
      include: 'node_modules/**',
    }),
  ],
};
