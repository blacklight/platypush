<template>
  <div class="action-tile-container">
    <div class="action-tile"
         :class="{ new: isNew }"
         ref="tile"
         @click="$refs.actionEditor.show">
      <div class="action-delete"
           title="Remove"
           v-if="withDelete && !readOnly"
           @click.stop="$emit('delete')">
        <i class="icon fas fa-xmark" />
      </div>

      <div class="action-name" v-if="name?.length">
        <span class="icon">
          <ExtensionIcon :name="name.split('.')[0]" size="1.5em" />
        </span>
        <span class="name">
          {{ name }}
        </span>
      </div>

      <div class="new-action" v-else>
        <i class="icon fas fa-plus" />&nbsp; Add Action
      </div>

      <div class="action-args" v-if="Object.keys(value.args || {})?.length">
        <div class="arg" v-for="(arg, name) in value.args" :key="name">
          <div class="arg-name">
            {{ name }}
          </div>

          <div class="arg-value">
            {{ arg }}
          </div>
        </div>
      </div>
    </div>

    <Draggable :element="tile"
               :disabled="readOnly"
               :value="value"
               @drag="$emit('drag', $event)"
               @drop="$emit('drop', $event)"
               v-if="draggable" />

    <Droppable :element="tile"
               :disabled="readOnly"
               @dragenter="$emit('dragenter', $event)"
               @dragleave="$emit('dragleave', $event)"
               @dragover="$emit('dragover', $event)"
               @drop="$emit('drop', $event)"
               v-if="draggable" />

    <div class="action-editor-container">
      <Modal ref="actionEditor" title="Edit Action">
        <ActionEditor :value="value"
                      :with-save="!readOnly"
                      @input="onInput"
                      v-if="this.$refs.actionEditor?.$data?.isVisible" />
      </Modal>
    </div>
  </div>
</template>

<script>
import ActionEditor from "@/components/Action/ActionEditor"
import Draggable from "@/components/elements/Draggable"
import Droppable from "@/components/elements/Droppable"
import ExtensionIcon from "@/components/elements/ExtensionIcon"
import Modal from "@/components/Modal"

export default {
  emits: [
    'delete',
    'drag',
    'dragenter',
    'dragleave',
    'dragover',
    'drop',
    'input',
  ],

  components: {
    ActionEditor,
    Draggable,
    Droppable,
    ExtensionIcon,
    Modal,
  },

  props: {
    draggable: {
      type: Boolean,
      default: true,
    },

    value: {
      type: Object,
      default: () => ({
        name: undefined,
        args: {},
        extraArgs: [],
        supportsExtraArgs: true,
      }),
    },

    withDelete: {
      type: Boolean,
      default: false,
    },

    readOnly: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      tile: null,
    }
  },

  computed: {
    isNew() {
      return !this.readOnly && !this.name?.length
    },

    name() {
      return this.value.name || this.value.action
    },
  },

  methods: {
    onInput(value) {
      if (!value || this.readOnly) {
        return
      }

      this.$emit('input', {
        ...this.value,
        name: value.action,
        args: value.args,
        extraArgs: value.extraArgs,
        supportsExtraArgs: value.supportsExtraArgs,
      })

      this.$refs.actionEditor.close()
    },
  },

  mounted() {
    this.tile = this.$refs.tile
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.action-tile-container {
  position: relative;

  .action-tile {
    min-width: 20em;
    background: $tile-bg;
    color: $tile-fg;
    display: flex;
    flex-direction: column;
    padding: 0.5em 1em;
    overflow: hidden;
    text-overflow: ellipsis;
    content: "";
    position: relative;
    border-radius: 1em;
    cursor: pointer;

    &:hover {
      background: $tile-hover-bg;
    }

    &.selected {
      background: $tile-hover-bg;
    }

    &.new {
      background: $tile-bg-3;

      &:hover {
        background: $tile-hover-bg-3;
      }
    }

    .action-delete {
      width: 1.5em;
      height: 1.5em;
      font-size: 1.25em;
      position: absolute;
      top: 0.25em;
      right: 0;
      opacity: 0.7;
      transition: opacity 0.25s ease-in-out;
      cursor: pointer;

      &:hover {
        opacity: 1;
      }
    }

    .action-name {
      display: inline-flex;
      font-size: 1.1em;
      font-weight: bold;
      font-family: monospace;
      align-items: center;

      .icon {
        width: 1.5em;
        height: 1.5em;
        margin-right: 0.75em;
      }
    }

    .new-action {
      font-style: italic;
    }

    .action-args {
      display: flex;
      flex-direction: column;
      margin-top: 0.5em;

      .arg {
        display: flex;
        flex-direction: row;
        align-items: center;
        margin-bottom: 0.5em;

        .arg-name {
          font-weight: bold;
          margin-right: 0.5em;
        }

        .arg-value {
          font-family: monospace;
          font-size: 0.9em;
          flex: 1;
        }
      }
    }
  }

  .action-editor-container {
    :deep(.modal-container) {
      @include until($tablet) {
        .modal {
          width: calc(100vw - 1em);

          .content {
            width: 100%;

            .body {
              width: 100%;
            }
          }
        }
      }

      .content .body {
        width: 80vw;
        height: 80vh;
        max-width: 800px;
        padding: 0;
      }

      .tabs {
        margin-top: 0;
      }

      .action-editor {
        height: 100%;
      }

      form {
        height: calc(100% - $tab-height);
        overflow: auto;
      }
    }
  }
}
</style>
