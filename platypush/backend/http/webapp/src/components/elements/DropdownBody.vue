<template>
  <div class="dropdown" :id="id" @click="$emit('click', $event)">
    <slot />
  </div>
</template>

<script>
export default {
  emits: ['click'],
  props: {
    id: {
      type: String,
    },

    keepOpenOnItemClick: {
      type: Boolean,
      default: false,
    },
  },
}
</script>

<style lang="scss" scoped>
.dropdown {
  position: absolute;
  width: max-content;
  background: $dropdown-bg;
  border-radius: .25em;
  box-shadow: $dropdown-shadow;
  display: flex;
  flex-direction: column;
  z-index: 2;
}

:deep(.dropdown-container) {
  button {
    width: 100%;
    height: 100%;
    color: $default-fg-2;
    background: $dropdown-bg;
    border: 0;
    padding: 0.75em 0.5em;
    text-align: left;
    letter-spacing: 0.01em;

    &:hover {
      background: $hover-bg;
      color: $default-fg-2;
    }

    .text {
      padding-left: 0.25em;
    }
  }
}
</style>
