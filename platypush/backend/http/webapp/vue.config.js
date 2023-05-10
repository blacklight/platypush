const httpProxy = {
  target: 'http://localhost:8008',
  changeOrigin: true
}

const wsProxy = {
  target: 'http://localhost:8008',
  changeOrigin: false,
  ws: true,
  onProxyReq: function(request) {
    console.log('===== HERE');
    console.log(request);
    request.setHeader('Origin', 'http://localhost:8008');
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

  devServer: {
    proxy: {
      '/execute': httpProxy,
      '/ws/events': wsProxy,
      '/ws/requests': wsProxy,
      '/static/*': httpProxy,
      '/auth': httpProxy,
      '/login': httpProxy,
      '/logout': httpProxy,
      '/register': httpProxy,
      '/camera/*': httpProxy,
      '/sound/*': httpProxy,
    }
  }
};
