<template>
  <div class="extension-icon" :style="{ width: `${size}`, height: `${size}` }">
    <a :href="docsUrl" target="_blank">
      <img :src="iconUrl" :alt="extensionName" :title="extensionName" />
    </a>
  </div>
</template>

<script>
export default {
  props: {
    name: {
      type: String,
      required: true,
    },

    size: {
      type: String,
      default: '1.75em',
    },
  },

  computed: {
    iconUrl() {
      return `https://static.platypush.tech/icons/${this.extensionName}-64.png`
    },

    extensionType() {
      return this.name.split('.')[0] == 'backend' ? 'backend' : 'plugin'
    },

    extensionName() {
      const words = this.name.split('.')
      if (words.length < 1)
        return this.name

      if (words[0] == 'backend')
        words.shift()

      return words.join('.')
    },

    docsUrl() {
      return `https://docs.platypush.tech/platypush/${this.extensionType}s/${this.extensionName}.html`
    },
  },
}
</script>

<style lang="scss" scoped>
.extension-icon {
  img {
    width: 100%;
    height: 100%;
  }
}
</style>
