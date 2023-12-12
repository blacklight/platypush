<template>
  <div class="file-selector-container">
    <div class="input">
      <input type="text"
             :value="value"
             :readonly="strict"
             @input="$emit('input', $event.target.value)" />

      <button type="button"
              title="Select a file"
              @click="$refs.fileSelectorModal.show()">
        <i class="fa fa-folder-open" />
      </button>
    </div>

    <Modal title="Select a file" ref="fileSelectorModal">
      <Browser :initialPath="path"
               @input="onValueChange($event)"
               @path-change="path = $event" />
    </Modal>
  </div>
</template>

<script>
import Modal from "@/components/Modal";
import Browser from "@/components/File/Browser";

export default {
  emits: ['input'],
  components: {
    Browser,
    Modal,
  },

  props: {
    value: {
      type: String,
    },

    strict: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      path: '/',
    }
  },

  methods: {
    onValueChange(value) {
      this.$emit('input', value)
    },

    onFileSelect(value) {
      if (value != null && (value.startsWith('/') || value.startsWith('file://')))
        this.path = value.split('/').slice(0, -1).join('/')
      else
        this.path = '/'

      this.$refs.fileSelectorModal.hide()
    },
  },

  watch: {
    value(value) {
      this.onFileSelect(value)
    },
  },

  mounted() {
    this.onFileSelect(this.value)
  },
}
</script>

<style lang="scss" scoped>
.file-selector-container {
  display: flex;
  flex-direction: column;

  .input {
    display: flex;
    flex-direction: row;
    align-items: stretch;

    input {
      flex-grow: 1;
      border-radius: 1em 0 0 1em;
      border-right: none;
    }

    button {
      border-radius: 0 1em 1em 0;
      border-left: none;
    }
  }

  :deep(.modal) {
    .body {
      width: 80vw;
      height: 80vh;
      max-width: 800px;
      padding: 0;

      .items {
        .item {
          padding: 1em 0.5em;
        }
      }
    }
  }
}
</style>
