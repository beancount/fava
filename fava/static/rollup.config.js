import commonjs from 'rollup-plugin-commonjs';
import copy from 'rollup-plugin-copy';
import css from 'rollup-plugin-css-only';
import json from 'rollup-plugin-json';
import nodeResolve from 'rollup-plugin-node-resolve';

export default {
  input: 'javascript/main.js',
  output: {
    file: 'gen/app.js',
    format: 'iife',
  },
  plugins: [
    nodeResolve(),
    json(),
    css(),
    copy({
      'node_modules/@typopro/web-fira-mono/TypoPRO-FiraMono-Medium.woff':
        'gen/FiraMono-Medium.woff',
      'node_modules/@typopro/web-fira-mono/TypoPRO-FiraMono-Regular.woff':
        'gen/FiraMono-Regular.woff',
      'node_modules/@typopro/web-fira-sans/TypoPRO-FiraSans-Medium.woff':
        'gen/FiraSans-Medium.woff',
      'node_modules/@typopro/web-fira-sans/TypoPRO-FiraSans-Regular.woff':
        'gen/FiraSans-Regular.woff',
      'node_modules/@typopro/web-source-code-pro/TypoPRO-SourceCodePro-Regular.woff':
        'gen/SourceCodePro-Regular.woff',
      'node_modules/@typopro/web-source-code-pro/TypoPRO-SourceCodePro-Semibold.woff':
        'gen/SourceCodePro-Semibold.woff',
      'node_modules/@typopro/web-source-serif-pro/TypoPRO-SourceSerifPro-Regular.woff':
        'gen/SourceSerifPro-Regular.woff',
      'node_modules/@typopro/web-source-serif-pro/TypoPRO-SourceSerifPro-Semibold.woff':
        'gen/SourceSerifPro-Semibold.woff',
    }),
    commonjs({
      include: 'node_modules/**',
    }),
  ],
};
