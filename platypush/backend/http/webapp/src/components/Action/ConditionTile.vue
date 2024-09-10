<template>
  <ListItem class="condition-tile"
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
          @click.stop="showConditionEditor = true"
          v-if="!isElse">
      <div class="tile-name">
        <span class="icon">
          <i class="fas fa-question" />
        </span>
        <span class="name">
          <span class="keyword">if</span> [
          <span class="code" v-text="value" /> ]
          <span class="keyword">then</span>
        </span>
      </div>
    </Tile>

    <Tile v-bind="tileConf.props"
          v-on="tileConf.on"
          :draggable="false"
          :read-only="true"
          @click="$emit('click')"
          v-else>
      <div class="tile-name">
        <span class="icon">
          <i class="fas fa-question" />
        </span>
        <span class="name">
          <span class="keyword">else</span>
        </span>
      </div>
    </Tile>

    <div class="condition-editor-container" v-if="showConditionEditor && !readOnly">
      <Modal title="Edit Condition"
             :visible="true"
             @close="showConditionEditor = false">
        <ConditionEditor :value="value"
                         ref="conditionEditor"
                         @input.prevent.stop="onConditionChange"
                         v-if="showConditionEditor" />
      </Modal>
    </div>
  </ListItem>
</template>

<script>
import ConditionEditor from "./ConditionEditor"
import ListItem from "./ListItem"
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
    ConditionEditor,
    ListItem,
    Modal,
    Tile,
  },

  props: {
    value: {
      type: String,
      required: true,
    },

    active: {
      type: Boolean,
      default: false,
    },

    isElse: {
      type: Boolean,
      default: false,
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
  },

  data() {
    return {
      dragging: false,
      showConditionEditor: false,
    }
  },

  methods: {
    onConditionChange(event) {
      this.showConditionEditor = false
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
