<template>
  <div class="actions-block" :class="{ hover }">
    <slot name="before" />

    <div class="actions-list-container" ref="actionsListContainer">
      <button class="collapse-button"
              @click="collapsed_ = !collapsed_"
              v-if="isCollapsed">
        <i class="fas fa-ellipsis-h" />
      </button>

      <div class="actions-list" :class="actionListClasses">
        <ActionsList :value="value[key]"
                     :dragging="dragging"
                     :has-else="hasElse"
                     :indent="indent"
                     :is-inside-loop="isInsideLoop"
                     :parent="value"
                     :read-only="readOnly"
                     @add-else="$emit('add-else')"
                     @collapse="collapsed_ = !collapsed_"
                     @drag="$emit('drag', $event)"
                     @dragend="$emit('dragend', $event); hover = false"
                     @dragenter="$emit('dragenter', $event)"
                     @dragleave="$emit('dragleave', $event); hover = false"
                     @dragover="$emit('dragover', $event)"
                     @drop="$emit('drop', $event); hover = false"
                     @input="$emit('input', $event); hover = false" />
      </div>
    </div>

    <slot name="after" />

    <Droppable :element="$refs.actionsListContainer"
               @dragenter="onDragEnter"
               @dragleave="onDragLeave"
               @drop="hover = false"
               v-if="!readOnly" />
  </div>
</template>

<script>
import { defineAsyncComponent } from "vue"
import Droppable from "@/components/elements/Droppable"
import Mixin from "./Mixin"

export default {
  name: 'ActionsBlock',
  mixins: [Mixin],
  emits: [
    'add-else',
    'drag',
    'dragend',
    'dragenter',
    'dragleave',
    'dragover',
    'drop',
    'input',
  ],

  components: {
    // Handle indirect circular dependency
    ActionsList: defineAsyncComponent(() => import('./ActionsList')),
    Droppable,
  },

  props: {
    value: {
      type: Object,
      required: true,
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
      default: false,
    },

    readOnly: {
      type: Boolean,
      default: false,
    },

    hasElse: {
      type: Boolean,
      default: false,
    },
  },

  computed: {
    actionListClasses() {
      return {
        hidden: this.isCollapsed,
        fold: this.folding,
        unfold: this.unfolding,
      }
    },

    condition() {
      return this.getCondition(this.key)
    },

    isCollapsed() {
      const transitioning = this.hover || this.folding || this.unfolding
      if (transitioning) {
        return false
      }

      if (this.collapsed_) {
        return true
      }

      return this.collapsed
    },

    key() {
      return this.getKey(this.value)
    },
  },

  data() {
    return {
      collapsed_: false,
      folding: false,
      hover: false,
      hoverTimeout: null,
      unfolding: false,
    }
  },

  watch: {
    collapsed_(value) {
      if (value) {
        this.folding = true
        setTimeout(() => {
          this.folding = false
        }, 300)
      } else {
        this.unfolding = true
        setTimeout(() => {
          this.unfolding = false
        }, 300)
      }
    },
  },

  methods: {
    onDragEnter() {
      if (this.hoverTimeout) {
        return
      }

      this.hoverTimeout = setTimeout(() => {
        this.hover = true
      }, 500)
    },

    onDragLeave() {
      if (this.hoverTimeout) {
        clearTimeout(this.hoverTimeout)
        this.hoverTimeout = null
      }

      this.hover = false
    },
  },
}
</script>

<style lang="scss" scoped>
.actions-block {
  .collapse-button {
    width: 100%;
    background: none !important;
    margin-left: 1em;
    font-size: 0.85em;
    text-align: left;
    border: none;
  }

  &.hover {
    .collapse-button {
      color: $default-hover-fg;
    }
  }
}
</style>
