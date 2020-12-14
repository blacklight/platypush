module.exports = {
  outputDir: "../dist",
  assetsDir: "static",
  css: {
    loaderOptions: {
      sass: {
        additionalData: `
          @import '~bulma';
          @import '~w3css/w3.css';
          @import "@/style/mixins.scss";
          @import "@/style/themes/light.scss";
          @import "@/style/layout.scss";
          @import "@/style/components.scss";
          @import "@/style/animations.scss";
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
