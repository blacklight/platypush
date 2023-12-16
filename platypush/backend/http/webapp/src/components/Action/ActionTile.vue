<template>
  <div class="action-tile" @click="$refs.actionEditor.show">
    <div class="action-delete" title="Remove" v-if="withDelete" @click.stop="$emit('delete')">
      <i class="icon fas fa-xmark" />
    </div>

    <div class="action-name" v-if="name?.length">
      {{ name }}
    </div>

    <div class="new-action" v-else>
      <i class="icon fas fa-plus" />&nbsp; New Action
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

  <div class="action-editor-container">
    <Modal ref="actionEditor" title="Edit Action">
      <ActionEditor :value="value" with-save @input="onInput"
                    v-if="this.$refs.actionEditor?.$data?.isVisible" />
    </Modal>
  </div>
</template>

<script>
import ActionEditor from "@/components/Action/ActionEditor"
import Modal from "@/components/Modal";

export default {
  emits: ['input', 'delete'],
  components: {
    ActionEditor,
    Modal,
  },

  props: {
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
  },

  computed: {
    name() {
      return this.value.name || this.value.action
    },
  },

  methods: {
    onInput(value) {
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
}
</script>

<style lang="scss" scoped>
@import "common";

.action-tile {
  min-width: 20em;
  max-height: 7.5em;
  background: $action-tile-bg;
  color: $action-tile-fg;
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
    color: $default-hover-fg;
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

    &:hover {
      opacity: 1;
    }
  }

  .action-name {
    font-size: 1.1em;
    font-weight: bold;
    font-family: monospace;
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
</style>
