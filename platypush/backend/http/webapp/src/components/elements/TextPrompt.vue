<template>
  <Modal ref="modal" :title="title">
    <form @submit.prevent="onConfirm">
      <div class="dialog-content">
        <slot />
        <input type="text" ref="input" v-model="value_" />
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

    visible: {
      type: Boolean,
      default: false,
    },

    value: {
      type: String,
      default: "",
    },
  },

  data() {
    return {
      value_: "",
      visible_: false,
    }
  },

  methods: {
    onConfirm() {
      this.$emit('input', this.value_)
      this.close()
    },

    open() {
      if (this.visible_)
        return

      this.value_ = this.value
      this.$refs.modal.show()
      this.visible_ = true
      this.focus()
    },

    close() {
      if (!this.visible_)
        return

      this.value_ = ""
      this.$refs.modal.hide()
      this.visible_ = false
    },

    show() {
      this.open()
    },

    hide() {
      this.close()
    },

    focus() {
      this.$nextTick(() => {
        this.$refs.input.focus()
      })
    },
  },

  watch: {
    visible(val) {
      if (val) {
        this.open()
      } else {
        this.close()
      }
    },
  },

  mounted() {
    this.visible_ = this.visible
    this.value_ = this.value || ""
    this.$nextTick(() => {
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
