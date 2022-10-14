<template>
  <Modal ref="modal" :title="title">
    <div class="dialog-content">
      <slot />
    </div>

    <div class="buttons">
      <button type="button" class="cancel-btn" @click="close" @touch="close">
        <i class="fas fa-xmark" /> &nbsp; Close
      </button>
    </div>
  </Modal>
</template>

<script>
import Modal from "@/components/Modal";

export default {
  emits: ['input', 'click', 'touch'],
  components: {Modal},
  props: {
    title: {
      type: String,
    },
  },

  methods: {
    show() {
      this.$refs.modal.show()
    },

    close() {
      this.$refs.modal.hide()
    },
  },
}
</script>

<style lang="scss" scoped>
:deep(.modal) {
  .dialog-content {
    padding: 1em;
  }

  .buttons {
    display: flex;
    flex-direction: row;
    justify-content: right;
    padding: 1em 0 1em 1em;
    border: 0;
    border-radius: 0;
    box-shadow: 0 -1px $default-shadow-color;

    button {
      padding: 0.5em 1em;
      border: 1px solid $border-color-2;
      border-radius: 1em;

      &:hover {
        background: $hover-bg;
      }
    }
  }
}
</style>
