<template>
  <ListItem class="return-tile"
            :value="value"
            :active="active"
            :read-only="readOnly"
            :spacer-bottom="spacerBottom"
            :spacer-top="spacerTop"
            @input="$emit('input', $event)">
    <Tile v-bind="tileConf.props"
          v-on="tileConf.on"
          @click.stop="showExprEditor = true">
      <div class="tile-name">
        <span class="icon">
          <i class="fas fa-angle-right" />
        </span>
        <span class="name">
          <span class="keyword">return</span> <span class="code" v-text="value" />
        </span>
      </div>
    </Tile>

    <div class="editor-container" v-if="showExprEditor && !readOnly">
      <Modal title="Edit Return"
             :visible="true"
             @close="showExprEditor = false">
        <ExpressionEditor :value="value"
                          :allow-empty="true"
                          :context="context"
                          :quote="true"
                          placeholder="Optional return value"
                          ref="exprEditor"
                          @input.prevent.stop="onExprChange"
                          v-if="showExprEditor">
          Value or Expression
        </ExpressionEditor>
      </Modal>
    </div>
  </ListItem>
</template>

<script>
import ExpressionEditor from "./ExpressionEditor"
import ListItem from "./ListItem"
import Mixin from "./Mixin"
import Modal from "@/components/Modal"
import Tile from "@/components/elements/Tile"

export default {
  mixins: [Mixin],
  emits: [
    'change',
    'click',
    'delete',
    'input',
  ],

  components: {
    ExpressionEditor,
    ListItem,
    Modal,
    Tile,
  },

  props: {
    value: {
      type: [String, Number, Boolean, Object, Array],
      default: '',
    },

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
  },

  computed: {
    tileConf() {
      return {
        props: {
          value: this.value,
          class: 'keyword',
          draggable: false,
          readOnly: this.readOnly,
          withDelete: !this.readOnly,
        },

        on: {
          delete: () => this.$emit('delete'),
          input: this.onInput,
        },
      }
    },
  },

  data() {
    return {
      showExprEditor: false,
    }
  },

  methods: {
    onExprChange(event) {
      this.showExprEditor = false
      if (this.readOnly) {
        return
      }

      const expr = event.target.value?.trim()
      event.target.value = expr
      this.$emit('change', expr)
    },

    onInput(value) {
      if (!value || this.readOnly) {
        return
      }

      this.$emit('input', value)
    },
  },
}
</script>
