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
                      :line="line"
                      :text="text"
                      :content-type="contentType"
                      :with-save="withSave"
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
import Utils from '@/Utils'

export default {
  emits: ['close', 'open', 'save'],
  mixins: [Modal, Utils],
  components: {
    ConfirmDialog,
    FileEditor,
    Modal,
  },

  props: {
    file: {
      type: String,
    },

    text: {
      type: String,
      default: '',
    },

    contentType: {
      type: String,
      default: 'text/plain',
    },

    isNew: {
      type: Boolean,
      default: false,
    },

    line: {
      type: [String, Number],
      default: null,
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
      this.setUrlArgs({ maximized: null })
      this.$emit('close')
    },
  },

  watch: {
    maximized() {
      this.setUrlArgs({ maximized: this.maximized })
    },
  },

  mounted() {
    this.maximized = !!this.getUrlArgs().maximized
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

$maximized-modal-header-height: 2.75em;

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
        min-width: 30em;
        max-height: calc(100vh - 2em);
      }

      .content {
        @extend .expand;
      }
    }

    &:not(.maximized) {
      :deep(.modal) {
        .body {
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

          .modal-body {
            height: 50em;
          }
        }
      }
    }

    &.maximized {
      :deep(.modal) {
        width: calc(100vw - 2em);
        height: calc(100vh - 2em);

        .content, .modal-body {
          width: 100%;
          height: 100%;
          max-height: 100%;
        }

        .header {
          height: $maximized-modal-header-height;
        }

        .body {
          height: calc(100% - #{$maximized-modal-header-height});
          max-height: 100%;
        }
      }
    }
  }

  .confirm-dialog-container {
    :deep(.modal) {
      width: 35em !important;
      height: 9em !important;
      max-width: 100%;
      max-height: 100%;

      .body {
        width: 100% !important;
        height: 100% !important;
        justify-content: center;
      }
    }
  }
}
</style>
