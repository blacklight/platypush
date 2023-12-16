<template>
  <div class="procedure-editor-container"
       :class="{dragging: dragItem != null}">
    <div class="procedure-editor">
      <form autocomplete="off" @submit.prevent="executeAction">
        <div class="name-editor-container" v-if="withName">
          <div class="row item">
            <div class="name">
              <label>
                <i class="icon fas fa-pen-to-square" />
                Name
              </label>
            </div>

            <div class="value">
              <input type="text" v-model="newValue.name" />
            </div>
          </div>
        </div>

        <div class="actions">
          <div class="row item" v-for="(action, index) in newValue.actions" :key="index">
            <div class="drop-target-container"
                 :class="{active: dropIndex === index}"
                 v-if="dragItem != null && dragItem > index"
                 @dragover.prevent="dropIndex = index"
                 @dragenter.prevent="dropIndex = index"
                 @dragleave.prevent="dropIndex = undefined"
                 @dragend.prevent="dropIndex = undefined"
                 @drop="onDrop(index)">
              <div class="drop-target" />
            </div>

            <div class="separator" v-else-if="dragItem != null && dragItem === index" />

            <ActionTile :value="action"
                        draggable with-delete
                        @drag="dragItem = index"
                        @drop="dragItem = undefined"
                        @input="editAction($event, index)"
                        @delete="deleteAction(index)" />

            <div class="drop-target-container"
                 :class="{active: dropIndex === index}"
                 @dragover.prevent="dropIndex = index"
                 @dragenter.prevent="dropIndex = index"
                 @dragleave.prevent="dropIndex = undefined"
                 @dragend.prevent="dropIndex = undefined"
                 @drop="onDrop(index)"
                 v-if="dragItem != null && dragItem < index">
              <div class="drop-target" />
            </div>

            <div class="separator" v-else-if="dragItem != null && dragItem === index" />
          </div>

          <div class="row item">
            <ActionTile :value="newAction" @input="addAction" />
          </div>
        </div>

        <!-- Structured response container -->
        <Response :response="response" :error="error" />
      </form>
    </div>
  </div>
</template>

<script>
import ActionTile from "@/components/Action/ActionTile"
import Response from "@/components/Action/Response"
import Utils from "@/Utils"

export default {
  mixins: [Utils],
  emits: ['input'],
  components: {
    ActionTile,
    Response,
  },

  props: {
    withName: {
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
      loading: false,
      running: false,
      response: undefined,
      error: undefined,
      actions: [],
      newValue: {...this.value},
      newAction: {},
      dragItem: undefined,
      dropIndex: undefined,
    }
  },

  methods: {
    onResponse(response) {
      this.response = (
        typeof response === 'string' ? response : JSON.stringify(response, null, 2)
      ).trim()

      this.error = undefined
    },

    onError(error) {
      this.response = undefined
      this.error = error
    },

    onDone() {
      this.running = false
    },

    emitInput() {
      this.$emit('input', this.newValue)
    },

    onDrop(index) {
      if (this.dragItem === undefined)
        return

      this.newValue.actions.splice(
        index, 0, this.newValue.actions.splice(this.dragItem, 1)[0]
      )

      this.emitInput()
    },

    executeAction() {
      if (!this.value.actions?.length)
        return

      this.running = true
      this.execute(this.value.actions).then(this.onResponse).catch(this.onError).finally(this.onDone)
    },

    editAction(action, index) {
      this.newValue.actions[index] = action
      this.emitInput()
    },

    addAction(action) {
      this.newValue.actions.push(action)
      this.emitInput()
    },

    deleteAction(index) {
      this.newValue.actions.splice(index, 1)
      this.emitInput()
    },
  },

  watch: {
    value: {
      immediate: true,
      deep: true,
      handler(value) {
        this.newValue = {...value}
      },
    },
  },
}
</script>

<style lang="scss" scoped>
.procedure-editor-container {
  display: flex;
  flex-direction: column;
  padding-top: 0.75em;

  .procedure-editor {
    width: 100%;
  }

  .actions {
    .item {
      margin-bottom: 0.75em;
    }

    .drop-target-container {
      width: 100%;
      height: 0.75em;
      display: flex;
      align-items: center;

      &.active {
        .drop-target {
          height: 0.5em;
          background: $tile-bg;
          border: none;
          opacity: 0.75;
        }
      }

      .drop-target {
        width: 100%;
        height: 2px;
        border: 1px solid $default-fg-2;
        border-radius: 0.25em;
        padding: 0 0.5em;
      }
    }
  }

  &.dragging {
    padding-top: 0;

    .actions {
      .item {
        margin-bottom: 0;
      }

      .separator {
        height: 0.75em;
      }
    }
  }
}
</style>
