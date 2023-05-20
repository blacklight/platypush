<template>
  <Modal ref="modal" :title="title">
    <div class="dialog-content">
      <slot />
    </div>

    <form class="buttons" @submit.prevent="onConfirm">
      <button type="submit" class="ok-btn" @click="onConfirm" @touch="onConfirm">
        <i class="fas fa-check" /> &nbsp; {{ confirmText }}
      </button>
      <button type="button" class="cancel-btn" @click="close" @touch="close">
        <i class="fas fa-xmark" /> &nbsp; {{ cancelText }}
      </button>
    </form>
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

    confirmText: {
      type: String,
      default: "OK",
    },

    cancelText: {
      type: String,
      default: "Cancel",
    },
  },

  methods: {
    onConfirm() {
      this.$emit('input')
      this.close()
    },

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
    border: 0;
    border-radius: 0;

    button {
      margin-right: 1em;
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
