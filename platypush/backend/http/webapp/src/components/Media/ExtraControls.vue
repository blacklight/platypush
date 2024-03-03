<template>
  <div class="extra-controls-container">
    <button @click="$emit('consume')" :class="{enabled: status.consume}" title="Toggle consume mode" v-if="buttons.consume">
      <i class="icon fa fa-utensils"></i>
    </button>
    <button @click="$emit('random')" :class="{enabled: status.random}" title="Toggle shuffle" v-if="buttons.random">
      <i class="icon fa fa-random"></i>
    </button>
    <button @click="$emit('repeat')" :class="{enabled: status.repeat}" title="Toggle repeat" v-if="buttons.repeat">
      <i class="icon fa fa-redo"></i>
    </button>
  </div>
</template>

<script>
export default {
  emits: ['consume', 'random', 'repeat'],
  props: {
    status: {
      type: Object,
      default: () => ({}),
    },

    buttons: {
      type: Object,
      default: () => ({}),
    },
  },
}
</script>

<style lang="scss" scoped>
.extra-controls-container {
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;

  button {
    margin: 0 .25em;
    padding: 0;
    background: none;
    border: 0;

    &.enabled {
      color: $selected-fg;
    }

    &:not(:disabled):hover {
      color: $default-hover-fg;
      opacity: 1;
    }
  }
}
</style>
