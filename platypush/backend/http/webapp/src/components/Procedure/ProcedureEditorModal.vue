<template>
  <div class="procedure-editor-modal-container">
    <Modal :title="title || value.name"
           :visible="visible"
           :uppercase="!value.name"
           :before-close="(() => $refs.editor?.checkCanClose())"
           ref="editorModal"
           @close="$emit('close')">
      <ProcedureEditor :procedure="value"
                       :read-only="isReadOnly"
                       :with-name="!isReadOnly"
                       :with-save="!isReadOnly"
                       :value="value"
                       :modal="isReadOnly ? null : (() => $refs.editorModal)"
                       ref="editor"
                       @input="$emit('input', $event)" />
    </Modal>
  </div>
</template>

<script>
import Modal from "@/components/Modal";
import ProcedureEditor from "@/components/Procedure/ProcedureEditor"

export default {
  mixins: [Modal, ProcedureEditor],
  emits: ['close', 'input'],
  components: {
    Modal,
    ProcedureEditor,
  },

  data: function() {
    return {
      args: {},
      defaultIconClass: 'fas fa-cogs',
      extraArgs: {},
      collapsed_: true,
      infoCollapsed: false,
      lastError: null,
      lastResponse: null,
      newArgName: '',
      newArgValue: '',
      runCollapsed: false,
      showConfirmDelete: false,
      showFileEditor: false,
      showProcedureEditor: false,
    }
  },

  computed: {
    isReadOnly() {
      return this.value.procedure_type && this.value.procedure_type !== 'db'
    },
  },

  methods: {
    // Proxy and delegate the Modal's methods
    open() {
      this.$refs.editorModal.open()
    },

    close() {
      this.$refs.editorModal.close()
    },

    show() {
      this.$refs.editorModal.show()
    },

    hide() {
      this.$refs.editorModal.hide()
    },

    toggle() {
      this.$refs.editorModal.toggle()
    },
  },

  watch: {
    collapsed: {
      immediate: true,
      handler(value) {
        this.collapsed_ = value
      },
    },

    selected: {
      immediate: true,
      handler(value) {
        this.collapsed_ = value
      },
    },

    showProcedureEditor(value) {
      if (!value) {
        this.$refs.editor?.reset()
      }
    },
  },

  mounted() {
    this.collapsed_ = !this.selected
  },
}
</script>

<style lang="scss" scoped>
.procedure-editor-modal-container {
  cursor: default;

  :deep(.modal-container) {
    .body {
      padding: 0;

      @include until($tablet) {
        width: calc(100vw - 2em);
      }

      @include from($tablet) {
        width: 50em;
      }
    }
  }
}
</style>
