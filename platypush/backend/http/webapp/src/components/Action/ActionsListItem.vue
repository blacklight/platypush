<template>
  <div class="row item action" :class="{ dragging }">
    <div class="spacer-wrapper" :class="{ hidden: !spacerTop }">
      <div class="spacer"
           :class="{ active }"
           ref="dropTargetTop">
        <div class="droppable-wrapper">
          <div class="droppable-container">
            <div class="droppable-frame">
              <div class="droppable" />
            </div>
          </div>
        </div>
      </div>

      <Droppable :element="$refs.dropTargetTop"
                 :disabled="readOnly"
                 @dragend.prevent="onDrop"
                 @dragenter.prevent="$emit('dragenterspacer', $event)"
                 @dragleave.prevent="$emit('dragleavespacer', $event)"
                 @dragover.prevent="$emit('dragoverspacer', $event)"
                 @drop="$emit('drop', $event)" />
    </div>

    <div class="spacer" v-if="dragging" />

    <ActionTile :value="value"
                :draggable="!readOnly"
                :read-only="readOnly"
                :with-delete="!readOnly"
                @contextmenu="$emit('contextmenu', $event)"
                @drag="onDragStart"
                @dragend.prevent="onDragEnd"
                @dragover.prevent="$emit('dragover', $event)"
                @drop="onDrop"
                @input="$emit('input', $event)"
                @delete="$emit('delete', $event)" />

    <div class="spacer" v-if="dragging" />

    <div class="spacer-wrapper" :class="{ hidden: !spacerBottom }">
      <div class="spacer" :class="{ active }" ref="dropTargetBottom">
        <div class="droppable-wrapper">
          <div class="droppable-container">
            <div class="droppable-frame">
              <div class="droppable" />
            </div>
          </div>
        </div>
      </div>

      <Droppable :element="$refs.dropTargetBottom"
                 :disabled="readOnly"
                 @dragend.prevent="onDrop"
                 @dragenter.prevent="$emit('dragenterspacer', $event)"
                 @dragleave.prevent="$emit('dragleavespacer', $event)"
                 @dragover.prevent="$emit('dragoverspacer', $event)"
                 @drop="onDrop" />
    </div>
  </div>
</template>

<script>
import ActionTile from "@/components/Action/ActionTile"
import Droppable from "@/components/elements/Droppable"
import Utils from "@/Utils"

export default {
  mixins: [Utils],
  emits: [
    'contextmenu',
    'delete',
    'drag',
    'dragend',
    'dragenter',
    'dragenterspacer',
    'dragleave',
    'dragleavespacer',
    'dragover',
    'dragoverspacer',
    'drop',
    'input',
  ],

  components: {
    ActionTile,
    Droppable,
  },

  props: {
    active: {
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
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      dragging: false,
      dragItem: undefined,
      dropIndex: undefined,
      newAction: {},
      spacerElements: {},
      visibleTopSpacers: {},
      visibleBottomSpacers: {},
    }
  },

  methods: {
    onDragStart(event) {
      this.dragging = true
      this.$emit('drag', event)
    },

    onDragEnd(event) {
      this.dragging = false
      this.$emit('dragend', event)
    },

    onDrop(event) {
      this.dragging = false
      this.$emit('drop', event)
    },
  },
}
</script>

<style lang="scss" scoped>
$spacer-height: 1em;

.action {
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
