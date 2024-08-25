<template>
  <div class="file-editor-root">
    <div class="file-editor-modal" :class="{ maximized }">
      <Modal v-bind="proxiedProperties"
             ref="modal"
             @close="onClose">
        <div class="modal-body">
          <FileEditor ref="fileEditor"
                      :file="file"
                      :is-new="isNew"
                      @save="$emit('save', $event)"
                      v-if="file" />
        </div>
      </Modal>

      <div class="confirm-dialog-container">
        <ConfirmDialog ref="confirmClose" @input="forceClose">
          This file has unsaved changes. Are you sure you want to close it?
        </ConfirmDialog>
      </div>
    </div>
  </div>
</template>

<script>
import ConfirmDialog from "@/components/elements/ConfirmDialog";
import FileEditor from "./Editor";
import Modal from "@/components/Modal";

export default {
  emits: ['close', 'open', 'save'],
  mixins: [Modal],
  components: {
    ConfirmDialog,
    FileEditor,
    Modal,
  },

  props: {
    file: {
      type: String,
      required: true,
    },

    isNew: {
      type: Boolean,
      default: false,
    },

    withSave: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      confirmClose: true,
      maximized: false,
    }
  },

  computed: {
    filename() {
      return this.file.split('/').pop() || 'Untitled'
    },

    headerButtons() {
      const buttons = []

      if (this.maximized) {
        buttons.push({
          title: 'Restore',
          icon: 'far fa-window-restore',
          action: () => this.maximized = false,
        })
      } else {
        buttons.push({
          title: 'Maximize',
          icon: 'far fa-window-maximize',
          action: () => this.maximized = true,
        })
      }

      return buttons
    },

    proxiedProperties() {
      const props = {...this.$props}
      delete props.file
      delete props.withSave
      props.buttons = this.headerButtons
      props.title = this.filename
      props.beforeClose = this.checkClose
      return props
    },
  },

  methods: {
    checkClose() {
      if (this.withSave && this.confirmClose && this.$refs.fileEditor.hasChanges) {
        this.$refs.confirmClose.open()
        return false
      }

      return true
    },

    forceClose() {
      this.confirmClose = false
      this.$refs.modal.close()
    },

    onClose() {
      this.$refs.fileEditor.reset()
      this.$emit('close')
    },
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

.file-editor-root {
  .file-editor-modal {
    :deep(.modal) {
      .body {
        display: flex;
        flex-direction: column;
        padding: 0;
      }

      .modal-body {
        width: 100%;
        height: 50em;
        min-width: 30em;
        max-height: calc(100vh - 2em);
      }
    }

    &:not(.maximized) {
      :deep(.body) {
        @include until($tablet) {
          width: calc(100vw - 2em);
        }

        @include from($tablet) {
          width: 40em;
          max-width: 100%;
        }

        @include from($desktop) {
          width: 100%;
          min-width: 50em;
        }
      }
    }

    &.maximized {
      :deep(.body) {
        width: 100vw;
        height: 100vh;
      }
    }
  }

  .confirm-dialog-container {
    :deep(.modal) {
      .content {
        .body {
          min-width: 30em;
          max-width: 100%;
        }
      }
    }
  }
}
</style>
