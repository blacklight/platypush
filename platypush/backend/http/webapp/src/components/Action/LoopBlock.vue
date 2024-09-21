<template>
  <div class="loop-block">
    <ActionsBlock :value="value"
                  :collapsed="collapsed"
                  :context="context_"
                  :dragging="isDragging"
                  :indent="indent"
                  :is-inside-loop="true"
                  :read-only="readOnly"
                  @input="onActionsChange"
                  @drag="$emit('drag', $event)"
                  @dragend="$emit('dragend', $event)"
                  @dragenter="$emit('dragenter', $event)"
                  @dragleave="$emit('dragleave', $event)"
                  @dragover="$emit('dragover', $event)"
                  @drop="$emit('drop', $event)">
      <template #before>
        <LoopTile v-bind="loopTileConf.props"
                  v-on="loopTileConf.on"
                  @input.prevent.stop
                  :spacer-top="spacerTop"
                  :spacer-bottom="false" />
      </template>

      <template #after>
        <EndBlockTile :value="`end ${type}`"
                      icon="fas fa-arrow-rotate-right"
                      :active="active"
                      :spacer-bottom="spacerBottom || dragging"
                      @drop="onDrop" />
      </template>
    </ActionsBlock>
  </div>
</template>

<script>
import ActionsBlock from "./ActionsBlock"
import EndBlockTile from "./EndBlockTile"
import LoopTile from "./LoopTile"
import Mixin from "./Mixin"

export default {
  name: 'LoopBlock',
  mixins: [Mixin],
  emits: [
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
    LoopTile,
    EndBlockTile,
  },

  props: {
    value: {
      type: Object,
      required: true,
    },

    type: {
      type: String,
      required: true,
    },

    active: {
      type: Boolean,
      default: false,
    },

    async: {
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

    indent: {
      type: Number,
      default: 0,
    },

    isInsideLoop: {
      type: Boolean,
      default: true,
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
    changeHandler() {
      if (this.type === 'for') {
        return this.onForChange
      }

      if (this.type === 'while') {
        return this.onWhileChange
      }

      return () => {}
    },

    context_() {
      const ctx = {...this.context}
      const iterator = this.loop?.iterator?.trim()
      if (iterator?.length) {
        ctx[iterator] = {
          source: 'for',
        }
      }

      return ctx
    },

    isDragging() {
      return this.dragging_ || this.dragging
    },

    key() {
      return this.getKey(this.value)
    },

    loop() {
      if (this.type === 'for') {
        return this.getFor(this.key)
      }

      if (this.type === 'while') {
        return {condition: this.getWhile(this.key)}
      }

      return {}
    },

    loopTileConf() {
      return {
        props: {
          ...this.loop,
          active: this.active,
          context: this.context_,
          readOnly: this.readOnly,
          spacerBottom: this.spacerBottom,
          spacerTop: this.spacerTop,
          type: this.type,
        },

        on: {
          change: this.changeHandler,
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
  },

  methods: {
    onActionsChange(value) {
      if (!this.key || this.readOnly) {
        return
      }

      this.$emit('input', { [this.key]: value })
    },

    onForChange(loop) {
      const iterable = loop?.iterable?.trim()
      const iterator = loop?.iterator?.trim()
      const async_ = loop?.async || false

      if (!this.key || this.readOnly || !iterable?.length || !iterator?.length) {
        return
      }

      const keyword = 'for' + (async_ ? 'k' : '')
      loop = `${keyword} ${iterator} in \${${iterable}}`
      this.$emit('input', { [loop]: this.value[this.key] })
    },

    onWhileChange(condition) {
      condition = condition?.trim()
      if (!this.key || this.readOnly || !condition?.length) {
        return
      }

      const loop = `while \${${condition}}`
      this.$emit('input', { [loop]: this.value[this.key] })
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
