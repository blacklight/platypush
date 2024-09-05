<template>
  <div class="actions" :class="{dragging: dragItem != null}">
    <div class="row item action" v-for="(action, index) in actions" :key="index">
      <ActionsListItem :value="action"
                       :active="dragItem != null"
                       :read-only="readOnly"
                       :spacer-bottom="visibleBottomSpacers[index]"
                       :spacer-top="visibleTopSpacers[index]"
                       :ref="`action-tile-${index}`"
                       @delete="deleteAction(index)"
                       @drag="dragItem = index"
                       @dragend.prevent="dragItem = null"
                       @dragenterspacer.prevent="dropIndex = index"
                       @dragleavespacer.prevent="dropIndex = undefined"
                       @dragover.prevent="onTileDragOver($event, index)"
                       @dragoverspacer.prevent="dropIndex = index"
                       @drop="onDrop(index)"
                       @input="editAction($event, index)" />
    </div>

    <div class="row item action">
      <ActionTile :value="newAction"
                  :draggable="false"
                  @input="addAction"
                  v-if="!readOnly" />
    </div>
  </div>
</template>

<script>
import ActionsListItem from "./ActionsListItem"
import ActionTile from "./ActionTile"
import Utils from "@/Utils"

export default {
  mixins: [Utils],
  emits: ['input'],
  components: {
    ActionsListItem,
    ActionTile,
  },

  props: {
    value: {
      type: Object,
      default: () => ({
        name: undefined,
        actions: [],
      }),
    },

    readOnly: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      actions: [],
      dragItem: undefined,
      dropIndex: undefined,
      newAction: {},
      spacerElements: {},
      visibleTopSpacers: {},
      visibleBottomSpacers: {},
    }
  },

  computed: {
    hasChanges() {
      return JSON.stringify(this.value) !== JSON.stringify(this.actions)
    },
  },

  methods: {
    onDrop(index) {
      if (this.dragItem == null || this.readOnly)
        return

      this.actions.splice(
        index, 0, this.actions.splice(this.dragItem, 1)[0]
      )

      this.dragItem = null
      this.dropIndex = null
    },

    onTileDragOver(event, index) {
      if (this.dragItem == null || this.readOnly || this.dragItem === index)
        return

      const dragOverTile = this.$refs[`action-tile-${index}`]?.[0]
      const dragOverTileEl = dragOverTile?.$el?.nextSibling
      if (!dragOverTileEl)
        return

      const rootTop = this.$el.getBoundingClientRect().top
      const cursorY = event.clientY - rootTop
      const dragOverTilePos = {
        top: dragOverTileEl.offsetTop,
        bottom: dragOverTileEl.offsetTop + dragOverTileEl.offsetHeight,
      }

      const dragOverTileSectionHeight = (dragOverTilePos.bottom - dragOverTilePos.top) / 3
      let cursorTileSection = null

      if (cursorY < dragOverTilePos.top + dragOverTileSectionHeight) {
        cursorTileSection = 'top'
      } else if (cursorY < dragOverTilePos.bottom - dragOverTileSectionHeight) {
        cursorTileSection = 'middle'
      } else {
        cursorTileSection = 'bottom'
      }

      if (cursorTileSection === 'middle') {
        this.dropIndex = null
        return
      }

      if (cursorTileSection === 'top' && index < this.dragItem) {
        this.dropIndex = index
      } else if (cursorTileSection === 'bottom' && index > this.dragItem) {
        if (index === this.actions.length - 1) {
          this.dropIndex = index + 1
        } else {
          this.dropIndex = index
        }
      }
    },

    editAction(action, index) {
      this.actions[index] = action
    },

    addAction(action) {
      this.actions.push(action)
    },

    deleteAction(index) {
      this.actions.splice(index, 1)
    },

    resetSpacers() {
      this.visibleTopSpacers = Object.keys(this.actions).reduce((acc, index) => {
        acc[index] = true
        return acc
      }, {})

      this.visibleBottomSpacers = {[this.actions.length - 1]: true}
      this.syncSpacers()
    },

    syncSpacers() {
      this.$nextTick(() => {
        this.spacerElements = Object.keys(this.actions).reduce((acc, index) => {
          acc[index] = this.$refs[`dropTarget_${index}`]?.[0]
          return acc
        }, {})
      })
    },

    syncValue() {
      if (!this.value || !this.hasChanges)
        return

      this.actions = this.value
    },
  },

  watch: {
    actions: {
      deep: true,
      handler(value) {
        this.$emit('input', value)
        this.resetSpacers()
      },
    },

    dragItem(value) {
      if (value == null || this.readOnly) {
        this.resetSpacers()
      } else {
        this.visibleTopSpacers = Object.keys(this.actions).reduce((acc, index) => {
          acc[index] = this.dragItem > index
          return acc
        }, {})

        this.visibleBottomSpacers = Object.keys(this.actions).reduce((acc, index) => {
          acc[index] = this.dragItem < index
          return acc
        }, {})

        this.syncSpacers()
      }
    },

    value: {
      immediate: true,
      deep: true,
      handler() {
        this.syncValue()
      },
    },
  },

  mounted() {
    this.syncValue()
    this.resetSpacers()
  },
}
</script>

<style lang="scss" scoped>
$spacer-height: 1em;

.actions {
  .action {
    margin: 0;
  }
}
</style>
