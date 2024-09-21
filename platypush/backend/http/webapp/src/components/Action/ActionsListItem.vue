<template>
  <ListItem class="action"
            :active="active"
            :dragging="dragging"
            :spacer-bottom="spacerBottom"
            :spacer-top="spacerTop"
            :value="value"
            v-on="componentsData.on">
    <ActionTile :value="value"
                :context="context"
                :draggable="!readOnly"
                :read-only="readOnly"
                :with-delete="!readOnly"
                v-on="componentsData.on"
                @contextmenu="$emit('contextmenu', $event)"
                @drag.stop="onDragStart"
                @delete="$emit('delete', $event)" />
  </ListItem>
</template>

<script>
import ActionTile from "@/components/Action/ActionTile"
import ListItem from "@/components/Action/ListItem"
import Utils from "@/Utils"

export default {
  mixins: [Utils],
  emits: [
    'contextmenu',
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
    ActionTile,
    ListItem,
  },

  props: {
    active: {
      type: Boolean,
      default: false,
    },

    context: {
      type: Object,
      default: () => ({}),
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
    }
  },

  computed: {
    componentsData() {
      return {
        on: {
          dragend: this.onDragEnd,
          dragover: this.onDragOver,
          drop: this.onDrop,
          input: this.onInput,
        }
      }
    },
  },

  methods: {
    onDragStart(event) {
      if (this.readOnly) {
        return
      }

      this.dragging = true
      this.$emit('drag', event)
    },

    onDragEnd(event) {
      event.stopPropagation()
      this.dragging = false
      this.$emit('dragend', event)
    },

    onDragOver(event) {
      event.stopPropagation()
      this.$emit('dragover', event)
    },

    onDrop(event) {
      if (this.readOnly) {
        return
      }

      event.stopPropagation()
      this.dragging = false
      this.$emit('drop', event)
    },

    onInput(value) {
      this.$emit('input', value)
    },
  },
}
</script>
