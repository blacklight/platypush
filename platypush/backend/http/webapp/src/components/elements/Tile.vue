<template>
  <div class="tile-container" :class="className">
    <div class="tile" ref="tile" @click="$emit('click', $event)">
      <div class="delete"
           title="Remove"
           v-if="withDelete"
           @click.stop="$emit('delete')">
        <i class="icon fas fa-xmark" />
      </div>

      <slot />
    </div>

    <Draggable :element="tile"
               :disabled="readOnly"
               :value="value"
               @drag="$emit('drag', $event)"
               @drop="$emit('drop', $event)"
               v-if="draggable" />

    <Droppable :element="tile"
               @dragenter="$emit('dragenter', $event)"
               @dragleave="$emit('dragleave', $event)"
               @dragover="$emit('dragover', $event)"
               @drop="$emit('drop', $event)"
               v-if="!readOnly" />
  </div>
</template>

<script>
import Draggable from "@/components/elements/Draggable"
import Droppable from "@/components/elements/Droppable"

export default {
  emits: [
    'click',
    'delete',
    'drag',
    'dragenter',
    'dragleave',
    'dragover',
    'drop',
  ],

  components: {
    Draggable,
    Droppable,
  },

  props: {
    className: {
      type: [String, Object],
      default: '',
    },

    draggable: {
      type: Boolean,
      default: true,
    },

    readOnly: {
      type: Boolean,
      default: false,
    },

    value: {
      type: [Object, String, Number, Boolean, Array],
    },

    withDelete: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      tile: undefined,
    }
  },

  mounted() {
    this.tile = this.$refs.tile
  },
}
</script>

<style lang="scss" scoped>
.tile-container {
  position: relative;

  .tile {
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

    .delete {
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
  }

  &.keyword {
    .tile {
      background: $tile-bg-2;

      &:hover {
        background: $tile-hover-bg-2;
      }
    }
  }

  &.add {
    .tile {
      background: $tile-bg-3;

      &:hover {
        background: $tile-hover-bg-3;
      }
    }
  }
}

:deep(.tile) {
  .tile-name {
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

  .keyword {
    color: $tile-keyword-fg;
  }

  .code {
    color: $tile-code-fg;
  }
}
</style>
