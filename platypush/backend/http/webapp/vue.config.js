module.exports = {
  outputDir: "../dist",
  assetsDir: "static",
  css: {
    loaderOptions: {
      sass: {
        additionalData: `
          @import '~bulma';
          @import '~w3css/w3.css';
          @import "@/style/common.scss";
        `
      }
    }
  },

  devServer: {
    proxy: {
      '/execute': {
        target: 'http://localhost:8008',
        changeOrigin: true,
      }
    }
  }
};
