<template>
  <ListItem class="set-variables-tile"
            :class="{active}"
            :value="value"
            :active="active"
            :read-only="readOnly"
            :spacer-bottom="spacerBottom"
            :spacer-top="spacerTop"
            v-on="dragListeners"
            @input="$emit('input', $event)">
    <Tile v-bind="tileConf.props"
          v-on="tileConf.on"
          :draggable="!readOnly"
          @click.stop="showEditor = true">
      <div class="tile-name">
        <span class="icon">
          <i class="fas fa-square-root-variable" />
        </span>
        <span class="name">
          <div class="keyword">set</div>
        </span>
      </div>

      <div class="variables">
        <div class="variable" v-for="(value, name) in value" :key="name">
          <span class="code name" v-text="name" />&nbsp;=
          <span class="code value" v-text="value" />
        </div>
      </div>
    </Tile>

    <div class="editor-container" v-if="showEditor && !readOnly">
      <Modal title="Set Variables"
             :visible="true"
             @close="showEditor = false">
        <form class="editor" @submit.prevent="onChange">
          <div class="variable" v-for="(v, i) in newValue" :key="i">
            <span class="name">
              <input type="text"
                     placeholder="Variable Name"
                     @blur="onBlur(i)"
                     @input.prevent.stop
                     v-model="newValue[i][0]">&nbsp;=
            </span>
            <span class="value">
              <input type="text"
                     placeholder="Value"
                     @input.prevent.stop
                     v-model="newValue[i][1]">
            </span>
          </div>

          <div class="variable">
            <span class="name">
              <input type="text"
                     placeholder="Variable Name"
                     ref="newVarName"
                     @input.prevent.stop
                     v-model="newVariable.name">&nbsp;=
            </span>
            <span class="value">
              <input type="text"
                     placeholder="Value"
                     ref="newVarValue"
                     @blur="onBlur(null)"
                     @input.prevent.stop
                     v-model="newVariable.value">
            </span>
          </div>

          <div class="buttons">
            <button type="submit" class="btn btn-primary">
              Save
            </button>
          </div>
        </form>
      </Modal>
    </div>
  </ListItem>
</template>

<script>
import ListItem from "./ListItem"
import Modal from "@/components/Modal"
import Tile from "@/components/elements/Tile"

export default {
  emits: [
    'click',
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
    ListItem,
    Modal,
    Tile,
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
      default: true,
    },

    spacerTop: {
      type: Boolean,
      default: true,
    },

    value: {
      type: Object,
      default: () => ({}),
    },
  },

  computed: {
    dragListeners() {
      return this.readOnly ? {} : {
          drag: this.onDragStart,
          dragend: this.onDragEnd,
          dragenter: (event) => this.$emit('dragenter', event),
          dragleave: (event) => this.$emit('dragleave', event),
          dragover: (event) => this.$emit('dragover', event),
          drop: this.onDrop,
      }
    },

    tileConf() {
      return {
        props: {
          value: this.value,
          class: 'keyword',
          readOnly: this.readOnly,
          withDelete: !this.readOnly,
        },

        on: {
          ...this.dragListeners,
          delete: () => this.$emit('delete'),
          input: this.onInput,
        },
      }
    },
  },

  data() {
    return {
      dragging: false,
      newValue: [],
      newVariable: {
        name: '',
        value: '',
      },
      showEditor: false,
    }
  },

  methods: {
    onChange() {
      this.showEditor = false
      if (this.readOnly) {
        return
      }

      const variables = this.newValue
      if (this.newVariable.name?.trim?.()?.length) {
        variables.push([this.newVariable.name, this.newVariable.value])
      }

      const args = variables.map(([name, value]) => {
          name = this.sanitizeName(name)
          try {
            value = JSON.parse(value)
          } catch (e) {
            value = value?.trim()
          }

          return [name, value]
        })
        .reduce((acc, [name, value]) => {
          if (!name?.length) {
            return acc
          }

          acc[name] = value
          return acc
        }, {})

      if (!Object.keys(args).length) {
        return
      }

      this.onInput(args)
    },

    onInput(value) {
      if (!value || this.readOnly) {
        return
      }

      this.$emit('input', {set: value})
    },

    onBlur(index) {
      if (this.readOnly) {
        return
      }

      if (index != null) {
        const name = this.sanitizeName(this.newValue[index][0])
        if (!name?.length) {
          this.newValue.splice(index, 1)
        } else {
          this.newValue[index][0] = name
        }
      } else {
        const name = this.sanitizeName(this.newVariable.name)
        const value = this.newVariable.value

        if (name?.length) {
          this.newValue.push([name, value])
          this.newVariable = {
            name: '',
            value: '',
          }

          this.$nextTick(() => {
            this.$refs.newVarName?.focus()
          })
        }
      }
    },

    onDragStart(event) {
      if (this.readOnly) {
        return
      }

      this.dragging = true
      this.$emit('drag', event)
    },

    onDragEnd(event) {
      this.dragging = false
      this.$emit('dragend', event)
    },

    onDrop(event) {
      this.dragging = false
      if (this.readOnly) {
        return
      }

      this.$emit('drop', event)
    },

    sanitizeName(name) {
      return name?.trim()?.replace(/[^\w_]/g, '_')
    },

    syncValue() {
      this.newValue = Object.entries(this.value)
    },
  },

  watch: {
    showEditor(value) {
      if (!value) {
        this.newVariable = {
          name: '',
          value: '',
        }
      } else {
        this.$nextTick(() => {
          this.$refs.newVarName?.focus()
        })
      }
    },

    value: {
      immediate: true,
      handler() {
        this.syncValue()
      },
    },
  },

  mounted() {
    this.syncValue()
    this.$nextTick(() => {
      this.$refs.newVarName?.focus()
    })
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.set-variables-tile {
  &.active {
    .spacer {
      display: none;
    }
  }

  .variables {
    margin-left: 2.5em;
  }

  .variable {
    .value {
      font-style: italic;
    }
  }

  .drag-spacer {
    height: 0;
  }

  .editor {
    display: flex;
    flex-direction: column;
    padding: 1em;

    .variable {
      display: flex;

      .value {
        flex: 1;

        input[type="text"] {
          width: 100%;
        }
      }
      
    }

    .buttons {
      margin: 1em;
    }
  }
}
</style>
