<template>
  <div class="condition-block">
    <ActionsBlock :value="value"
                  :collapsed="collapsed"
                  :context="context"
                  :dragging="isDragging"
                  :has-else="hasElse"
                  :is-inside-loop="isInsideLoop"
                  :indent="indent"
                  :read-only="readOnly"
                  @input="onActionsChange"
                  @add-else="$emit('add-else')"
                  @drag="$emit('drag', $event)"
                  @dragend="$emit('dragend', $event)"
                  @dragenter="$emit('dragenter', $event)"
                  @dragleave="$emit('dragleave', $event)"
                  @dragover="$emit('dragover', $event)"
                  @drop="$emit('drop', $event)">
      <template #before>
        <ConditionTile :value="condition"
                       v-bind="conditionTileConf.props"
                       v-on="conditionTileConf.on"
                       @input.prevent.stop
                       :spacer-top="spacerTop"
                       :spacer-bottom="false"
                       v-if="condition && !isElse" />

        <ConditionTile value="else"
                       v-bind="conditionTileConf.props"
                       v-on="conditionTileConf.on"
                       :is-else="true"
                       :spacer-top="spacerTop"
                       :spacer-bottom="false"
                       v-else-if="isElse" />
      </template>

      <template #after>
        <EndBlockTile value="end if"
                      icon="fas fa-question"
                      :active="active"
                      :spacer-bottom="spacerBottom || dragging_"
                      @drop="onDrop"
                      v-if="isElse || !hasElse" />
      </template>
    </ActionsBlock>
  </div>
</template>

<script>
import ActionsBlock from "./ActionsBlock"
import ConditionTile from "./ConditionTile"
import EndBlockTile from "./EndBlockTile"
import Mixin from "./Mixin"

export default {
  name: 'ConditionBlock',
  mixins: [Mixin],
  emits: [
    'add-else',
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
    ActionsBlock,
    ConditionTile,
    EndBlockTile,
  },

  props: {
    value: {
      type: Object,
      required: true,
    },

    active: {
      type: Boolean,
      default: false,
    },

    collapsed: {
      type: Boolean,
      default: false,
    },

    dragging: {
      type: Boolean,
      default: false,
    },

    hasElse: {
      type: Boolean,
      default: false,
    },

    indent: {
      type: Number,
      default: 0,
    },

    isElse: {
      type: Boolean,
      default: false,
    },

    isInsideLoop: {
      type: Boolean,
      default: false,
    },

    readOnly: {
      type: Boolean,
      default: false,
    },

    spacerBottom: {
      type: Boolean,
      default: false,
    },

    spacerTop: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      dragging_: false,
    }
  },

  computed: {
    condition() {
      return this.getCondition(this.key)
    },

    conditionTileConf() {
      return {
        props: {
          active: this.active,
          context: this.context,
          readOnly: this.readOnly,
          spacerBottom: this.spacerBottom,
          spacerTop: this.spacerTop,
        },

        on: {
          change: this.onConditionChange,
          delete: (event) => this.$emit('delete', event),
          drag: this.onDragStart,
          dragend: this.onDragEnd,
          dragenterspacer: (event) => this.$emit('dragenter', event),
          dragleavespacer: (event) => this.$emit('dragleave', event),
          dragover: (event) => this.$emit('dragover', event),
          dragoverspacer: (event) => this.$emit('dragoverspacer', event),
          drop: this.onDrop,
        },
      }
    },

    isDragging() {
      return this.dragging_ || this.dragging
    },

    key() {
      return this.getKey(this.value)
    },
  },

  methods: {
    onActionsChange(value) {
      if (!this.key || this.readOnly) {
        return
      }

      this.$emit('input', { [this.key]: value })
    },

    onConditionChange(condition) {
      if (!this.key || this.readOnly || !condition?.length) {
        return
      }

      condition = `if \${${condition.trim()}}`
      this.$emit('input', { [condition]: this.value[this.key] })
    },

    onDragStart(event) {
      if (this.readOnly) {
        return
      }

      this.dragging_ = true
      this.$emit('drag', event)
    },

    onDragEnd(event) {
      this.dragging_ = false
      this.$emit('dragend', event)
    },

    onDrop(event) {
      if (this.readOnly) {
        return
      }

      this.dragging_ = false
      this.$emit('drop', event)
    },
  },
}
</script>

<style lang="scss" scoped>
:deep(.condition-block) {
  .end-if-container {
    margin-bottom: 1em;
  }
}
</style>
