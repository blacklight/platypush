<template>
  <button class="copy-button"
          ref="copyButton"
          title="Copy to clipboard"
          @click.prevent="copy"
          @input.prevent="copy">
    <i class="fas fa-clipboard" />
  </button>
</template>

<script>
import Utils from "@/Utils"

export default {
  name: "CopyButton",
  emits: ['input', 'click'],
  mixins: [Utils],
  props: {
    text: {
      type: String,
    },
  },

  methods: {
    async copy(event) {
      if (this.text?.length)
        await this.copyToClipboard(this.text)

      this.$emit(event.type, event)
    },
  },
}
</script>

<style lang="scss" scoped>
.copy-button {
  position: absolute;
  top: 0;
  right: 0.5em;
  margin: 0;
  padding: 0 !important;
  background: none;
  color: $code-dark-fg;
  border: none;
  padding: 0.5em;
  font-size: 1.5em;
  cursor: pointer;
  z-index: 1;
}
</style>
