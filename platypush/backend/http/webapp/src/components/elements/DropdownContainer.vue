<template>
  <div class="dropdown-container" />
</template>

<script>
import { bus } from "@/bus";

export default {
  methods: {
    onOpen(component) {
      if (!component?.$el)
        return

      if (!component.keepOpenOnItemClick)
        this.onClose()

      this.$el.appendChild(component.$el)
    },

    onClose() {
      this.$el.innerHTML = ''
    },
  },

  mounted() {
    bus.on('dropdown-open', this.onOpen)
    bus.on('dropdown-close', this.onClose)
  },
}
</script>

<style lang="scss" scoped>
.dropdown-container {
  :deep(.dropdown) {
    border: $default-border-2;
  }
}
</style>
