const webpack = require('webpack');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

const extractDefault = new ExtractTextPlugin('theme_default.css', { allChunks: true });
const extractAlternative = new ExtractTextPlugin('theme_alternative.css', { allChunks: true });

module.exports = {
  entry: {
    app: './javascript/main.js',
    editor: './javascript/editor.js',
    theme_default: './sass/theme_default.scss',
    theme_alternative: './sass/theme_alternative.scss',
  },
  output: {
    path: `${__dirname}/gen`,
    filename: '[name].js',
  },
  module: {
    loaders: [
      {
        test: /theme_default\.scss$/,
        loader: extractDefault.extract('style-loader', 'css-loader!sass-loader'),
      },
      {
        test: /theme_alternative\.scss$/,
        loader: extractAlternative.extract('style-loader', 'css-loader!sass-loader'),
      },
      {
        test: /\.(ttf|eot|svg|woff(2)?)(\?[a-z0-9]+)?$/,
        loader: 'file-loader',
      },
      {
        test: /\.js?$/,
        exclude: /(node_modules)/,
        loader: 'babel?presets[]=es2015',
      },
    ],
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
    }),
    extractDefault,
    extractAlternative,
  ],
};
