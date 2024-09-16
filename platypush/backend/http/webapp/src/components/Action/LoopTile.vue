<template>
  <ListItem class="loop-tile"
            :value="value"
            :active="active"
            :read-only="readOnly"
            :spacer-bottom="spacerBottom"
            :spacer-top="spacerTop"
            v-on="dragListeners"
            @input="$emit('input', $event)">
    <div class="drag-spacer" v-if="dragging && !spacerTop">&nbsp;</div>

    <Tile v-bind="tileConf.props"
          v-on="tileConf.on"
          :draggable="!readOnly"
          @click.stop="showLoopEditor = true">
      <div class="tile-name">
        <span class="icon">
          <i class="fas fa-arrow-rotate-left" />
        </span>
        <span class="name" v-if="type === 'for'">
          <span class="keyword">for<span v-if="async">k</span></span> <span class="code" v-text="iterator" />
          <span class="keyword"> in </span> [
          <span class="code" v-text="iterable" /> ]
        </span>

        <span class="name" v-else-if="type === 'while'">
          <span class="keyword">while</span> [
          <span class="code" v-text="condition" /> ]
        </span>
      </div>
    </Tile>

    <div class="editor-container" v-if="showLoopEditor && !readOnly">
      <Modal title="Edit Loop"
             :visible="true"
             @close="showLoopEditor = false">
        <LoopEditor :iterator="iterator"
                    :iterable="iterable"
                    :async="async"
                    @change="onLoopChange"
                    v-if="showLoopEditor && type === 'for'">
          Loop
        </LoopEditor>

        <ExpressionEditor :value="condition"
                          @input.prevent.stop="onConditionChange"
                          v-else-if="showLoopEditor && type === 'while'">
          Loop Condition
        </ExpressionEditor>
      </Modal>
    </div>
  </ListItem>
</template>

<script>
import ExpressionEditor from "./ExpressionEditor"
import ListItem from "./ListItem"
import LoopEditor from "./LoopEditor"
import Modal from "@/components/Modal"
import Tile from "@/components/elements/Tile"

export default {
  emits: [
    'change',
    'click',
    'delete',
    'drag',
    'dragend',
    'dragenter',
    'dragleave',
    'dragover',
    'drop',
    'input',
  ],

  components: {
    ExpressionEditor,
    LoopEditor,
    ListItem,
    Modal,
    Tile,
  },

  props: {
    active: {
      type: Boolean,
      default: false,
    },

    async: {
      type: Boolean,
      default: false,
    },

    condition: {
      type: String,
    },

    iterator: {
      type: String,
    },

    iterable: {
      type: String,
    },

    readOnly: {
      type: Boolean,
      default: false,
    },

    spacerBottom: {
      type: Boolean,
      default: true,
    },

    spacerTop: {
      type: Boolean,
      default: true,
    },

    type: {
      type: String,
      required: true,
    },
  },

  computed: {
    dragListeners() {
      return this.readOnly ? {} : {
          drag: this.onDragStart,
          dragend: this.onDragEnd,
          dragenter: (event) => this.$emit('dragenter', event),
          dragleave: (event) => this.$emit('dragleave', event),
          dragover: (event) => this.$emit('dragover', event),
          drop: this.onDrop,
      }
    },

    tileConf() {
      return {
        props: {
          value: this.value,
          class: 'keyword',
          readOnly: this.readOnly,
          withDelete: !this.readOnly,
        },

        on: {
          ...this.dragListeners,
          delete: () => this.$emit('delete'),
          input: this.onInput,
        },
      }
    },

    value() {
      return `for ${this.iterator} in ${this.iterable}`
    },
  },

  data() {
    return {
      dragging: false,
      showLoopEditor: false,
    }
  },

  methods: {
    onConditionChange(event) {
      this.showLoopEditor = false
      if (this.readOnly) {
        return
      }

      const condition = event.target.value?.trim()
      if (!condition?.length) {
        return
      }

      event.target.value = condition
      this.$emit('change', condition)
    },

    onLoopChange(event) {
      this.showLoopEditor = false
      if (this.readOnly) {
        return
      }

      this.$emit('change', event)
    },

    onInput(value) {
      if (!value || this.readOnly) {
        return
      }

      this.$emit('input', value)
    },

    onDragStart(event) {
      if (this.readOnly) {
        return
      }

      this.dragging = true
      this.$emit('drag', event)
    },

    onDragEnd(event) {
      this.dragging = false
      this.$emit('dragend', event)
    },

    onDrop(event) {
      this.dragging = false
      if (this.readOnly) {
        return
      }

      this.$emit('drop', event)
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.action-tile {
  .condition {
    font-style: italic;
  }

  .drag-spacer {
    height: 0;
  }
}
</style>
