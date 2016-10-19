const ExtractTextPlugin = require('extract-text-webpack-plugin');

const extractDefault = new ExtractTextPlugin('theme_default.css', { allChunks: true });

module.exports = {
  entry: {
    app: './javascript/main.js',
    theme_default: './sass/theme_default.scss',
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
    extractDefault,
  ],
};
