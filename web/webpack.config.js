// const path = require('path');

// module.exports = {
//   entry: './front-end/javascript/index.js',  // path to our input file
//   output: {
//     filename: 'index-bundle.js',  // output bundle file name
//     path: path.resolve(__dirname, './static'),  // path to our Django static directory
//   },
//   module: {
//     rules: [
//       {
//         test: /\.(js|jsx)$/,
//         exclude: /node_modules/,
//         loader: "babel-loader",
//         options: { presets: ["@babel/preset-env", "@babel/preset-react"] }
//       },
//     ]
//   },
// };

var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  context: __dirname,

  entry: './mysite/polls/static/js/index',

  output: {
      path: path.resolve('./mysite/polls/static/bundles/'),
      filename: "[name]-[hash].js",
  },

  plugins: [
    new BundleTracker({filename: './mysite/webpack-stats.json'}),
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: ['babel-loader']
      }
    ]
  },
  resolve: {
    extensions: ['*', '.js', '.jsx']
  }

};

