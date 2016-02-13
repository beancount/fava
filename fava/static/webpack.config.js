var webpack = require('webpack');
var path = require('path');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
  entry: {
    'app': './javascript/main.js',
    'clipboard': './javascript/clipboard.js',
    'editor': './javascript/editor.js',
    'journal': './javascript/journal.js',
    'styles': './sass/styles.scss'
  },
  output: {
    path: __dirname + '/gen',
    filename: '[name].js'
  },
  module: {
    loaders: [
      {
        test: /\.scss$/,
        loader: ExtractTextPlugin.extract('style-loader', 'css-loader!sass-loader')
      },
      {
        test: [/ace-builds.*/, /.*ace-mode-beancount.*/],
        loader: 'script-loader'
      }
    ]
  },
  plugins: [
    new webpack.optimize.UglifyJsPlugin(),
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
    }),
    new ExtractTextPlugin('styles.css', {
      allChunks: true
    })
  ],
  //for handlebars
  node: {
      fs: 'empty'
  }
}
