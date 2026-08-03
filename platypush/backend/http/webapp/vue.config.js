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
  lintOnSave: false,
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
    workboxOptions: {
      skipWaiting: true,
      clientsClaim: true,
      runtimeCaching: [
        {
          urlPattern: /\/plugin\/.*\/icon/,
          handler: 'CacheFirst',
          options: {
            cacheName: 'plugin-icons',
            expiration: {
              maxEntries: 200,
              maxAgeSeconds: 30 * 24 * 60 * 60,  // 30 days
            },
          },
        },
      ],
    },
  },

  devServer: {
    proxy: {
      '^/auth': httpProxy,
      '^/camera/': httpProxy,
      '^/execute': httpProxy,
      '^/file': httpProxy,
      '^/logo.svg': httpProxy,
      '^/logout': httpProxy,
      '^/media/': httpProxy,
      '^/otp': httpProxy,
      '^/sound/': httpProxy,
      '^/tokens': httpProxy,
      '^/ws/': wsProxy,
    }
  }
};
