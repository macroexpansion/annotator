module.exports = {
  publicPath: '/tagging/',
  devServer: {
    disableHostCheck: true,
    proxy: {
      "^/api": {
        target: "http://webserver:5000/api",
        changeOrigin: true,
        pathRewrite: {
          "^/api": ""
        }
      },
      "^/socket.io": {
        target: "http://webserver:5000/socket.io",
        ws: true,
        changeOrigin: true,
        pathRewrite: {
          "^/socket.io": ""
        }
      }
    }
  },
  configureWebpack: {
    performance: {
      hints: false
    },
    optimization: {
      splitChunks: {
        minSize: 10000,
        maxSize: 250000,
      }
    }
  },
  lintOnSave: undefined,
  runtimeCompiler: true
};
