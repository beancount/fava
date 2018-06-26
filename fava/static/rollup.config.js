import buble from 'rollup-plugin-buble';
import commonjs from 'rollup-plugin-commonjs';
import copy from 'rollup-plugin-copy';
import json from 'rollup-plugin-json';
import nodeResolve from 'rollup-plugin-node-resolve';

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
    buble({
      exclude: 'css/**',
      transforms: {
        generator: false,
        forOf: false,
      },
    }),
    copy({
      'node_modules/codemirror/lib/codemirror.css': 'gen/codemirror/lib-codemirror.css',
      'node_modules/codemirror/addon/fold/foldgutter.css': 'gen/codemirror/addon-fold-foldgutter.css',
      'node_modules/codemirror/addon/dialog/dialog.css': 'gen/codemirror/addon-dialog-dialog.css',
      'node_modules/codemirror/addon/hint/show-hint.css': 'gen/codemirror/addon-hint-show-hint.css',
      'node_modules/@typopro/web-fira-mono/TypoPRO-FiraMono-Medium.woff': 'gen/FiraMono-Medium.woff',
      'node_modules/@typopro/web-fira-mono/TypoPRO-FiraMono-Regular.woff': 'gen/FiraMono-Regular.woff',
      'node_modules/@typopro/web-fira-sans/TypoPRO-FiraSans-Medium.woff': 'gen/FiraSans-Medium.woff',
      'node_modules/@typopro/web-fira-sans/TypoPRO-FiraSans-Regular.woff': 'gen/FiraSans-Regular.woff',
      'node_modules/@typopro/web-source-code-pro/TypoPRO-SourceCodePro-Regular.woff': 'gen/SourceCodePro-Regular.woff',
      'node_modules/@typopro/web-source-code-pro/TypoPRO-SourceCodePro-Semibold.woff': 'gen/SourceCodePro-Semibold.woff',
      'node_modules/@typopro/web-source-serif-pro/TypoPRO-SourceSerifPro-Regular.woff': 'gen/SourceSerifPro-Regular.woff',
      'node_modules/@typopro/web-source-serif-pro/TypoPRO-SourceSerifPro-Semibold.woff': 'gen/SourceSerifPro-Semibold.woff',
    }),
    commonjs({
      include: 'node_modules/**',
    }),
  ],
};
