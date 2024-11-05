<template>
  <div class="row item list-item" :class="itemClass">
    <div class="spacer-wrapper" :class="{ hidden: !spacerTop }">
      <div class="spacer top" :class="{ active }" ref="dropTargetTop">
        <div class="droppable-wrapper">
          <div class="droppable-container">
            <div class="droppable-frame">
              <div class="droppable" />
            </div>
          </div>
        </div>
      </div>

      <Droppable :element="$refs.dropTargetTop" :disabled="readOnly" v-on="droppableData.top.on" />
    </div>

    <div class="spacer top" v-if="dragging" />

    <slot />

    <div class="spacer bottom" v-if="dragging" />

    <div class="spacer-wrapper" :class="{ hidden: !spacerBottom }">
      <div class="spacer bottom" :class="{ active }" ref="dropTargetBottom">
        <div class="droppable-wrapper">
          <div class="droppable-container">
            <div class="droppable-frame">
              <div class="droppable" />
            </div>
          </div>
        </div>
      </div>

      <Droppable :element="$refs.dropTargetBottom" :disabled="readOnly" v-on="droppableData.bottom.on" />
    </div>
  </div>
</template>

<script>
import Droppable from "@/components/elements/Droppable"
import Utils from "@/Utils"

export default {
  mixins: [Utils],
  emits: [
    'contextmenu',
    'dragend',
    'dragenter',
    'dragleave',
    'dragover',
    'drop',
  ],

  components: {
    Droppable,
  },

  props: {
    active: {
      type: Boolean,
      default: false,
    },

    className: {
      type: [String, Object],
      default: '',
    },

    dragging: {
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
      default: true,
    },

    value: {
      type: [String, Number, Boolean, Object, Array],
      required: true,
    },
  },

  computed: {
    droppableData() {
      return ['bottom', 'top'].reduce((acc, key) => {
        acc[key] = {
          on: {
            dragend: this.onDragEnd,
            dragenter: this.onDragEnter,
            dragleave: this.onDragLeave,
            dragover: this.onDragOver,
            drop: this.onDrop,
          },
        }

        return acc
      }, {})
    },

    itemClass() {
      return {
        dragging: this.dragging,
        ...(this.className?.trim ? { [this.className]: true } : (this.className || {})),
      }
    },
  },

  methods: {
    onDragEnd(event) {
      this.$emit('dragend', event)
    },

    onDragEnter(event) {
      this.$emit('dragenter', event)
    },

    onDragLeave(event) {
      this.$emit('dragleave', event)
    },

    onDragOver(event) {
      this.$emit('dragover', event)
    },

    onDrop(event) {
      this.$emit('drop', event)
    },
  },
}
</script>

<style lang="scss" scoped>
$spacer-height: 1em;

.list-item {
  margin: 0;

  .spacer {
    height: $spacer-height;

    &.active {
      border-top: 1px dashed transparent;
      border-bottom: 1px dashed transparent;

      .droppable-frame {
        border: 1px dashed $selected-fg;
        border-radius: 0.5em;
      }
    }

    &.selected {
      height: 5em;
      padding: 0.5em 0;

      .droppable-frame {
        height: 100%;
        margin: 0.5em 0;
        padding: 0.1em;
        border: 2px dashed $ok-fg;
      }

      .droppable {
        height: 100%;
        background: $play-btn-fg;
        border: none;
        box-shadow: none;
        border-radius: 1em;
        opacity: 0.5;
      }
    }
  }

  .droppable-wrapper,
  .droppable-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
  }

  .droppable-container {
    .droppable-frame {
      width: 100%;
      height: 1px;
      opacity: 0.5;
    }

    .droppable {
      width: 100%;
      opacity: 0.8;
    }
  }
}
</style>
