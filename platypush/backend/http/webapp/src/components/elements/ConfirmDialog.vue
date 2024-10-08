<template>
  <Modal ref="modal" :visible="visible" :title="title" @close="close">
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
  emits: ['input', 'click', 'close', 'touch'],
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

    visible: {
      type: Boolean,
      default: false,
    },
  },

  methods: {
    onConfirm() {
      this.$emit('input')
      this.close()
    },

    open() {
      this.$refs.modal?.show()
    },

    close() {
      this.$refs.modal?.hide()
      this.$emit('close')
    },

    show() {
      this.open()
    },

    hide() {
      this.close()
    },
  },

  watch: {
    visible: {
      immediate: true,
      handler(val) {
        if (val) {
          this.open()
        } else {
          this.close()
        }
      },
    },
  },
}
</script>

<style lang="scss" scoped>
:deep(.modal) {
  .dialog-content {
    padding: 1em;
  }

  .body {
    padding: 1.5em;
  }

  .buttons {
    display: flex;
    flex-direction: row;
    justify-content: right;
    margin-bottom: 1em;
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
