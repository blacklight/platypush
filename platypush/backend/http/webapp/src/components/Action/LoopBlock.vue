<template>
  <div class="loop-block">
    <ActionsBlock :value="value"
                  :collapsed="collapsed"
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
        <EndBlockTile value="end for"
                      icon="fas fa-arrow-rotate-right"
                      :active="active"
                      :spacer-bottom="spacerBottom"
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
    loop() {
      return this.getFor(this.key)
    },

    loopTileConf() {
      return {
        props: {
          ...this.loop,
          active: this.active,
          readOnly: this.readOnly,
          spacerBottom: this.spacerBottom,
          spacerTop: this.spacerTop,
        },

        on: {
          change: this.onLoopChange,
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

    onLoopChange(loop) {
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
