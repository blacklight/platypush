module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
  },
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended',
  ],
  plugins: [],
  rules: {
    'vue/multi-word-component-names': 0,
  },
}
