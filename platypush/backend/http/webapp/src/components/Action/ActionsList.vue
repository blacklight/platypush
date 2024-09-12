<template>
  <div class="actions-list">
    <div class="indent-spacers" v-if="indent > 0">
      <div class="indent-spacer" @click="onCollapse">
        <div class="left side" />
        <div class="right side" />
      </div>
    </div>

    <div class="actions" :class="{dragging: isDragging}">
      <div class="row item action"
           v-for="(action, index) in visibleActions"
           :key="index">
        <ConditionBlock v-bind="componentsData[index].props"
                        v-on="componentsData[index].on"
                        :collapsed="collapsedBlocks[index]"
                        :dragging="isDragging"
                        @add-else="addElse"
                        v-if="conditions[index]" />

        <ConditionBlock v-bind="componentsData[index].props"
                        v-on="componentsData[index].on"
                        :collapsed="collapsedBlocks[index]"
                        :dragging="isDragging"
                        :is-else="true"
                        v-else-if="elses[index]" />

        <ReturnTile v-bind="componentsData[index].props"
                    :value="returnValue"
                    @change="editReturn($event)"
                    @delete="deleteAction(index)"
                    v-else-if="isReturn(action)" />

        <ActionsListItem v-bind="componentsData[index].props"
                         v-on="componentsData[index].on"
                         v-else-if="isAction(action) && !collapsed" />
      </div>

      <div class="row item action add-action-container" v-if="visibleAddButtons.action">
        <ListItem :active="isDragging"
                  :readOnly="false"
                  :spacerBottom="false"
                  :spacerTop="!newValue.length"
                  :value="newAction"
                  @drop="onDrop(0, $event)">
          <ActionTile :value="newAction"
                      :draggable="false"
                      @input="addAction" />
        </ListItem>
      </div>

      <div class="add-buttons-expander" v-if="showAddButtonsExpander">
        <button @click.stop.prevent="collapseAddButtons = !collapseAddButtons">
          <i class="fas" :class="collapseAddButtons ? 'fa-angle-down' : 'fa-angle-up'" />
        </button>
      </div>

      <div class="extra-add-buttons fade-in" v-if="showAddButtons">
        <div class="row item action add-return-container" v-if="visibleAddButtons.return">
          <AddTile icon="fas fa-angle-right" title="Add Return" @click="addReturn" />
        </div>

        <div class="row item action add-if-container" v-if="visibleAddButtons.condition">
          <AddTile icon="fas fa-question" title="Add Condition" @click="addCondition" />
        </div>

        <div class="row item action add-else-container" v-if="visibleAddButtons.else">
          <AddTile icon="fas fa-question" title="Add Else" @click="$emit('add-else')" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ActionsListItem from "./ActionsListItem"
import ActionTile from "./ActionTile"
import AddTile from "./AddTile"
import ConditionBlock from "./ConditionBlock"
import ListItem from "./ListItem"
import Mixin from "./Mixin"
import ReturnTile from "./ReturnTile"
import Utils from "@/Utils"

export default {
  name: 'ActionsList',
  mixins: [Mixin, Utils],
  emits: [
    'add-else',
    'change',
    'collapse',
    'drag',
    'dragend',
    'dragenter',
    'dragleave',
    'dragover',
    'drop',
    'input',
    'reset',
  ],

  components: {
    ActionsListItem,
    ActionTile,
    AddTile,
    ConditionBlock,
    ListItem,
    ReturnTile,
  },

  props: {
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

    hasElse: {
      type: Boolean,
      default: false,
    },

    parent: {
      type: Object,
      default: null,
    },

    readOnly: {
      type: Boolean,
      default: false,
    },

    value: {
      type: Object,
      default: () => ({
        name: undefined,
        actions: [],
      }),
    },
  },

  data() {
    return {
      collapseAddButtons: true,
      newValue: [],
      dragIndices: undefined,
      initialValue: undefined,
      newAction: {},
      spacerElements: {},
    }
  },

  computed: {
    collapsedBlocks() {
      return this.newValue.reduce((acc, action, index) => {
        if (!this.isActionsBlock(action)) {
          return acc
        }

        if (!this.isDragging) {
          acc[index] = this.collapsed
          return acc
        }

        if (this.elses[index]) {
          acc[index] = this.dragBlockIndex === index - 1
        } else {
          acc[index] = this.dragBlockIndex === index
        }

        return acc
      }, {})
    },

    componentsData() {
      return this.newValue.map((action, index) => {
        let data = {
          props: {
            value: action,
            active: this.isDragging,
            readOnly: this.readOnly,
            ref: `action-tile-${index}`,
            spacerBottom: this.visibleBottomSpacers[index],
            spacerTop: this.visibleTopSpacers[index],
          },

          on: {
            delete: () => this.deleteAction(index),
            drag: (event) => this.onDragStart(index, event),
            dragend: (event) => this.onDragEnd(event),
            dragenter: (event) => this.onDragEnter(index, event),
            dragleave: (event) => this.onDragLeave(index, event),
            dragover: (event) => this.onDragOver(event),
            drop: (event) => {
              try {
                this.onDrop(index, event)
              } finally {
                this.isDragging = false
              }
            },
            input: (value) => this.editAction(value, index),
          }
        }

        if (
          this.getCondition(action) &&
          this.newValue[index + 1] &&
          this.isElse(this.newValue[index + 1])
        ) {
          data.props.hasElse = true
        }

        if (this.isActionsBlock(action)) {
          data.props.indent = this.indent + 1
        }

        return data
      })
    },

    conditions() {
      return this.newValue?.reduce?.((acc, action, index) => {
        const condition = this.getCondition(action)
        if (condition) {
          acc[index] = {
            condition,
            actions: action[Object.keys(action)[0]],
          }
        }

        return acc
      }, {}) || {}
    },

    dragBlockIndex() {
      if (this.dragIndex == null) {
        return
      }

      // Return an index only if the dragged item is the actual actions block
      // and not one of its children.
      if (!(this.dragIndices?.length === 1 && this.dragIndices[0] === this.dragIndex)) {
        return
      }

      // Return an index only if the dragged item is an actions block.
      if (!this.isActionsBlock(this.newValue[this.dragIndex])) {
        return
      }

      return this.dragIndex
    },

    isDragging: {
      get() {
        return this.dragging || (this.dragIndices?.length || 0) > 0
      },
      set(value) {
        if (!value) {
          this.dragIndices = null
        }
      },
    },

    elses() {
      return this.newValue?.reduce?.((acc, action, index) => {
        if (this.isElse(action) && this.conditions[index - 1]) {
          acc[index] = action[Object.keys(action)[0]]
        }

        return acc
      }, {}) || {}
    },

    hasChanges() {
      return this.newStringValue !== this.stringValue
    },

    stringValue() {
      return JSON.stringify(this.value)
    },

    newStringValue() {
      return JSON.stringify(this.newValue)
    },

    dragIndex() {
      if (!this.isDragging) {
        return
      }

      return this.dragIndices?.[0]
    },

    returnIndex() {
      const ret = this.newValue?.reduce?.((acc, action, index) => {
        if (acc >= 0)
          return acc

        if (this.isReturn(action))
          return index

        return acc
      }, -1)

      return ret >= 0 ? ret : null
    },

    returnValue() {
      if (this.returnIndex == null)
        return ''

      const ret = this.newValue[this.returnIndex]
      if (ret == null)
        return ''

      let retValue = null
      if (Array.isArray(ret))
        retValue = ret.length === 1 ? ret[0].match(/^return\s*(.*)$/)?.[1] : ret
      else
        retValue = ret.return

      return retValue || ''
    },

    showAddButtons() {
      return (
        this.newValue.length === 0 || !this.collapseAddButtons
      )
    },

    showAddButtonsExpander() {
      return (
        !this.readOnly &&
        this.newValue?.length > 0 &&
        Object.entries(this.visibleAddButtons).filter(
          ([key, value]) => value && key != 'action'
        ).length > 1
      )
    },

    stopIndex() {
      return this.returnIndex
    },

    visibleActions() {
      return this.newValue.reduce((acc, action, index) => {
        if (this.stopIndex != null && index > this.stopIndex)
          return acc

        if (
          this.conditions[index] ||
          this.elses[index] ||
          this.isAction(action) ||
          this.isReturn(action)
        ) {
          acc[index] = action
        }

        return acc
      }, {})
    },

    visibleAddButtons() {
      return {
        action: !this.readOnly && !this.collapsed && this.stopIndex == null,
        return: !this.readOnly && !this.collapsed && this.stopIndex == null,
        condition: !this.readOnly && !this.collapsed && this.stopIndex == null,
        else: (
          !this.readOnly &&
          !this.collapsed &&
          this.parent &&
          this.getCondition(this.parent) &&
          !this.hasElse &&
          this.stopIndex == null
        ),
      }
    },

    visibleTopSpacers() {
      const dragIndex = this.dragIndex
      return this.newValue.reduce((acc, tile, index) => {
        acc[index] = (
          !this.isElse(tile) && (
            dragIndex == null ||
            dragIndex > index || (
              dragIndex === index &&
              this.dragIndices.length > 1
            )
          )
        )

        return acc
      }, {})
    },

    visibleBottomSpacers() {
      const dragIndex = this.dragIndex
      return this.newValue.reduce((acc, _, index) => {
        acc[index] = (
          (
            dragIndex != null && (
              dragIndex < index || (
                dragIndex === index &&
                this.dragIndices.length > 1
              )
            )
          ) || (
            dragIndex == null &&
            index === this.newValue.length - 1
          )
        )

        return acc
      }, {})
    },
  },

  methods: {
    onDragStart(index, event) {
      if (this.readOnly)
        return

      if (Array.isArray(event)) {
        event = [index, ...event]
      } else {
        event = [index]
      }

      this.dragIndices = event
      this.$emit('drag', event)
    },

    onDragEnd() {
      this.isDragging = false
      this.$emit('dragend')
    },

    onDragEnter(index, event) {
      if (!this.isDragging || this.readOnly) {
        return
      }

      event.stopPropagation()
      this.$emit('dragenter', index)
    },

    onDragLeave(index, event) {
      if (!this.isDragging || this.readOnly) {
        return
      }

      event.stopPropagation()
      this.$emit('dragleave', index)
    },

    onDragOver(event) {
      this.$emit('dragover', event)
    },

    onDrop(dropIndex, event) {
      if (!this.isDragging || event == null || dropIndex == null || this.readOnly) {
        return
      }

      event.stopPropagation()
      let dropIndices = []

      if (!event.detail?.length) {
        dropIndices = [dropIndex]
      } else {
        dropIndices = [dropIndex, ...event.detail]
      }

      event = new CustomEvent(
        'drop', {
          bubbles: false,
          cancelable: true,
          detail: dropIndices,
        }
      )

      if (this.indent > 0) {
        // If the current drop location is within a nested block, then we need to
        // bubble up the drop event to the parent block, until we reach the top block.
        this.$emit('drop', event)
        return
      }

      // If we are at the root level, then we have the full picture of the underlying
      // data structure, and we can perform the drop operation directly.
      const dragIndex = this.dragIndices.slice(-1)[0]
      dropIndex = event.detail.slice(-1)[0]

      // Get the parent blocks of the dragged and dropped items.
      const dragParent = this.getParentBlock(this.dragIndices)
      const dropParent = this.getParentBlock(dropIndices)
      if (!(dragParent && dropParent)) {
        return
      }

      const dragItem = dragParent?.[dragIndex]
      const dropItem = dropParent?.[dropIndex]
      if (!dragItem) {
        return
      }

      // If the dragged item is a condition, then we need to update the else block as well.
      const draggedItems = (
        this.getCondition(dragItem) && this.isElse(dragParent[dragIndex + 1]) ? 2 : 1
      )

      // If the drop location is an else block, then the target needs to be the next
      // slot, or we'll break the if-else chain.
      if (this.isElse(dropItem)) {
        dropIndex += 1
      }

      dropParent.splice(
        dropIndex, 0, ...dragParent.splice(dragIndex, draggedItems)
      )

      // Emit the drop event to the parent block, so that it can update its
      // view of the data structure.
      this.$emit('input', this.newValue)
    },

    onCollapse() {
      this.$emit('collapse')
    },

    getParentBlock(indices) {
      indices = [...indices]
      let parent = this.newValue
      while (parent && indices.length > 1) {
        parent = parent[indices.shift()]

        if (parent) {
          const blockKey = this.getKey(parent)
          if (blockKey) {
            parent = parent[blockKey]
          }
        }
      }

      return parent
    },

    editAction(event, index) {
      if (event?.target && event.stopPropagation) {
        // If the event is a native event, then we need to stop the propagation,
        // otherwise the event will be caught by the parent element. If the parent
        // is a modal, then the modal will be closed, making it impossible to edit
        // text fields in the action tiles.
        event.stopPropagation()
        return
      }

      this.newValue[index] = event
      this.$emit('input', this.newValue)
    },

    addAction(action) {
      this.newValue.push(
        {
          ...action,
          action: action.name || action.action,
        }
      )
    },

    addCondition() {
      this.newValue.push({ 'if ${True}': [] })
      this.selectLastExprEditor()
    },

    addReturn() {
      this.newValue.push({ 'return': null })
      this.selectLastExprEditor()
    },

    editReturn(value) {
      this.newValue[this.returnIndex] = { 'return': value?.length ? value : null }
    },

    selectLastExprEditor() {
      this.$nextTick(() => {
        const newTile = this.$refs[`action-tile-${this.newValue.length - 1}`]?.[0]
        if (!newTile) {
          return
        }

        const newTileElement = newTile.$el?.querySelector('.tile')
        if (!newTileElement) {
          return
        }

        newTileElement.click()
        this.$nextTick(() => {
          const exprEditor = newTile.$el?.querySelector('.expr-editor-container')
          if (!exprEditor) {
            return
          }

          const input = exprEditor.querySelector('input[type="text"]')
          if (!input) {
            return
          }

          input.value = ''
          input.focus()
        })
      })
    },

    addElse() {
      this.newValue.push({ 'else': [] })
    },

    deleteAction(index) {
      // If the action is a condition, then we need to also remove the else block
      const items = (
        this.getCondition(this.newValue[index]) && this.isElse(this.newValue?.[index + 1])
      ) ? 2 : 1

      const el = this.$refs[`action-tile-${index}`]?.[0]?.$el
      if (el) {
        el.classList.add('shrink')
        setTimeout(() => {
          el.classList.remove('shrink')
          this.newValue.splice(index, items)
        }, 300)
      } else {
        this.newValue.splice(index, items)
      }
    },

    syncSpacers() {
      this.$nextTick(() => {
        this.spacerElements = Object.keys(this.newValue).reduce((acc, index) => {
          acc[index] = this.$refs[`dropTarget_${index}`]?.[0]
          return acc
        }, {})
      })
    },

    syncValue() {
      if (!this.value || !this.hasChanges)
        return

      this.newValue = this.value
    },
  },

  watch: {
    newValue: {
      deep: true,
      handler(value) {
        this.$emit('input', value)
        this.syncSpacers()
      },
    },

    dragIndices() {
      this.syncSpacers()
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
    this.syncSpacers()
  },
}
</script>

<style lang="scss" scoped>
.actions-list {
  display: flex;
  flex-direction: row;

  .actions {
    flex: 1;

    .action {
      margin: 0;
    }

    .add-action-container {
      margin-bottom: 0.5em;
    }
  }

  .spacer {
    height: 1em;
  }

  .indent-spacers {
    display: flex;
    flex-direction: row;

    .indent-spacer {
      width: 1.5em;
      height: 100%;
      margin: 0;
      cursor: pointer;

      .side {
        width: 0.75em;
        height: 100%;

        &.left {
          border-right: 1px solid $selected-fg;
        }
      }

      &:hover {
        .side.left {
          border-right: 1px solid $tile-code-fg;
        }
      }
    }
  }

  .add-buttons-expander {
    width: 100%;
    height: 1em;
    margin: -0.5em 0 0.5em 0;

    button {
      width: 100%;
      height: 100%;
      background: none;
      display: flex;
      align-items: center;
      justify-content: center;
      border: none;
      margin: 0;
      padding: 0.5em 0 0 0;

      &:hover {
        color: $default-hover-fg;
      }
    }
    display: flex;
  }
}
</style>
