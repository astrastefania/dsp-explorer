var path = require("path")
var webpack = require('webpack')
var CommonsChunkPlugin = require("webpack/lib/optimize/CommonsChunkPlugin");
var BundleTracker = require('webpack-bundle-tracker');
var CleanObsoleteChunks = require('webpack-clean-obsolete-chunks');

module.exports = {

    entry: {
        dashboard: path.resolve(__dirname, 'dashboard/static/js')
        // enter a new entry point here
    },
    output: {
        path: path.join(__dirname, "static/bundles"),
        publicPath: '/static/bundles/',
        filename: "[name]-[chunkhash].js"
    },
    module : {
        rules: [
            {   test: /\.html?$/, loader: ["html-loader"] },
            {
                test: /\.css?$/,
                loaders: ["style-loader", "css-loader"]
            },
            {
                test: /\.scss?$/,
                loaders: ["style-loader", "css-loader", "sass-loader"]
            },
            {
                test: /\.js?$/, loader: 'babel-loader' ,
                exclude:  /node_modules/,
                query: {
                    presets: [ 'es2015' , 'stage-0' ],
                }
            },
            {
                test: /\.(png|woff|woff2|eot|ttf|svg|json)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                loader: 'file-loader?limit=100000&name=../fonts/[hash].[ext]'

            }
        ]
    },
    plugins: [
        new CommonsChunkPlugin({
            filename: "commons-[chunkhash].js",
            name: "commons"
        }),
        new BundleTracker(),
        new CleanObsoleteChunks()
    ]
}