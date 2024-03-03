<template>
  <button @click="$emit(status.state === 'play' ? 'pause' : 'play')"
          :title="status.state === 'play' ? 'Pause' : 'Play'">
    <i class="icon play-pause fa fa-pause" v-if="status.state === 'play'"></i>
    <i class="icon play-pause fa fa-play" v-else></i>
  </button>
</template>

<script>
export default {
  emits: ['play', 'pause'],
  props: {
    status: {
      type: Object,
      default: () => ({}),
    },
  },
}
</script>

<style lang="scss" scoped>
button {
  font-size: 1.75em;
  background: transparent;
  color: $play-btn-fg;
  padding: 0 !important;
  border: none;

  &:hover {
    color: $play-btn-hover-fg;
  }
}
</style>
