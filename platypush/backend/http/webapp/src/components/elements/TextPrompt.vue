<template>
  <Modal ref="modal" :title="title">
    <form @submit.prevent="onConfirm">
      <div class="dialog-content">
        <slot />
        <input type="text" ref="input" />
      </div>

      <div class="buttons">
        <button type="submit" class="ok-btn" @click="onConfirm" @touch="onConfirm">
          <i class="fas fa-check" /> &nbsp; {{ confirmText }}
        </button>
        <button type="button" class="cancel-btn" @click="close" @touch="close">
          <i class="fas fa-xmark" /> &nbsp; {{ cancelText }}
        </button>
      </div>
    </form>
  </Modal>
</template>

<script>
import Modal from "@/components/Modal";

export default {
  emits: ['input'],
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
      this.$emit('input', this.$refs.input.value)
      this.close()
    },

    show() {
      this.$refs.modal.show()
    },

    close() {
      this.$refs.modal.hide()
    },
  },

  mounted() {
    this.$nextTick(() => {
      this.$refs.input.value = ""
      this.$refs.input.focus()
    })
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

form {
  display: flex;
  flex-direction: column !important;

  .buttons {
    flex-direction: row !important;
  }
}

</style>
