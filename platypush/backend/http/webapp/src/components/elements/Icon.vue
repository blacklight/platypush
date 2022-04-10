<template>
  <div class="icon-container">
    <img class="icon" :src="url" :alt="alt" v-if="url?.length">
    <i class="icon" :class="className" v-else-if="className?.length" />
  </div>
</template>

<script>
export default {
  props: {
    class: {
      type: String,
    },
    url: {
      type: String,
    },
    alt: {
      type: String,
      default: '',
    },
  },

  computed: {
    className() {
      return this.class
    }
  }
}
</script>

<style lang="scss" scoped>
.icon-container {
  display: inline-flex;
  width: $icon-container-size;
  justify-content: center;
  text-align: center;

  .icon {
    width: 1em;
    height: 1em;
  }
}
</style>
