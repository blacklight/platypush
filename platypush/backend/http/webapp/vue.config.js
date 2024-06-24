const httpProxy = {
  target: 'http://127.0.0.1:8008',
  changeOrigin: true
}

const wsProxy = {
  target: 'http://127.0.0.1:8008',
  changeOrigin: false,
  ws: true,
  onProxyReq: function(request) {
    request.setHeader('Origin', 'http://127.0.0.1:8008');
  },
}

module.exports = {
  lintOnSave: true,
  outputDir: "dist",
  assetsDir: "static",
  css: {
    loaderOptions: {
      sass: {
        additionalData: `
          @import '~w3css/w3.css';
          @import "@/style/common.scss";
        `
      }
    }
  },

  pwa: {
    name: 'Platypush',
    themeColor: '#ffffff',
  },

  devServer: {
    proxy: {
      '^/ws/events': wsProxy,
      '^/ws/requests': wsProxy,
      '^/ws/shell': wsProxy,
      '^/execute': httpProxy,
      '^/file': httpProxy,
      '^/auth': httpProxy,
      '^/camera/': httpProxy,
      '^/sound/': httpProxy,
      '^/media/': httpProxy,
      '^/logo.svg': httpProxy,
    }
  }
};
