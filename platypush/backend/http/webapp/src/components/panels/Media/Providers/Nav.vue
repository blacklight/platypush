<template>
  <div class="nav">
    <span class="path">
      <span class="back token" title="Back" @click="$emit('back')">
        <i class="fas fa-home" />
      </span>

      <span class="separator">
        <i class="fas fa-chevron-right" />
      </span>
    </span>

    <span class="path" v-for="(token, index) in path" :key="index">
      <span class="token" :title="token.title" @click="onClick(token)">
        <i class="icon" :class="icon" v-if="icon = token.icon?.['class']" />
        <span v-if="token.title">{{ token.title }}</span>
      </span>

      <span class="separator"
            v-if="(index > 0 || path.length > 1) && index < path.length - 1">
        <i class="fas fa-chevron-right" />
      </span>
    </span>
  </div>
</template>

<script>
export default {
  emit: ['back'],

  props: {
    path: {
      type: Array,
      default: () => [],
    },
  },

  methods: {
    onClick(token) {
      if (token.click)
        token.click()
    },
  },
}
</script>

<style lang="scss" scoped>
@import "../style.scss";

.nav {
  overflow-x: auto !important;
  overflow-y: hidden !important;

  .path .token .icon {
    margin-right: 0.5em;
  }
}
</style>
