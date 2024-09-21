<template>
  <div class="args-body" @keydown="onKeyDown">
    <div class="args-list"
         v-if="Object.keys(action.args).length || action.supportsExtraArgs">
      <!-- Supported action arguments -->
      <div class="arg" :key="name" v-for="name in Object.keys(action.args)">
        <label>
          <ContextAutocomplete :value="action.args[name].value"
                               :disabled="running"
                               :items="contextAutocompleteItems"
                               :placeholder="name"
                               :quote="true"
                               :select-on-tab="false"
                               @input="onArgEdit(name, $event)"
                               @blur="onSelect(name)"
                               @focus="onSelect(name)" />
          <span class="required-flag" v-if="action.args[name].required">*</span>
        </label>

        <Argdoc :name="selectedArg"
                :args="action.args[selectedArg]"
                :doc="selectedArgdoc"
                :loading="loading"
                is-mobile
                v-if="selectedArgdoc && selectedArg && name === selectedArg" />
      </div>

      <!-- Extra action arguments -->
      <div class="extra-args" v-if="Object.keys(action.extraArgs).length">
        <div class="arg extra-arg" :key="i" v-for="(arg, i) in action.extraArgs">
          <label class="col-5">
            <input type="text"
                   class="action-extra-arg-name"
                   placeholder="Name"
                   :disabled="running"
                   :value="arg.name"
                   @input="onExtraArgNameEdit(i, $event.target.value)">
          </label>
          <label class="col-6">
            <ContextAutocomplete :value="arg.value"
                                 :disabled="running"
                                 :items="contextAutocompleteItems"
                                 :quote="true"
                                 :select-on-tab="false"
                                 placeholder="Value"
                                 @input="onExtraArgValueEdit(i, $event.detail)" />
          </label>
          <label class="col-1 buttons">
            <button type="button" class="action-extra-arg-del" title="Remove argument" @click="$emit('remove', i)">
              <i class="fas fa-trash" />
            </button>
          </label>
        </div>
      </div>

      <div class="add-arg" v-if="action.supportsExtraArgs">
        <button type="button" title="Add an argument" @click="onArgAdd">
          <i class="fas fa-plus" />
        </button>
      </div>
    </div>

    <Argdoc :name="selectedArg"
            :args="action.args[selectedArg]"
            :doc="selectedArgdoc"
            :loading="loading"
            v-if="selectedArgdoc && selectedArg" />
  </div>
</template>

<script>
import Argdoc from "./Argdoc"
import ContextAutocomplete from "./ContextAutocomplete"
import Mixin from "./Mixin"

export default {
  mixins: [Mixin],
  components: {
    Argdoc,
    ContextAutocomplete,
  },

  emits: [
    'add',
    'arg-edit',
    'extra-arg-name-edit',
    'extra-arg-value-edit',
    'input',
    'remove',
    'select',
  ],

  props: {
    action: Object,
    loading: Boolean,
    running: Boolean,
    selectedArg: String,
    selectedArgdoc: String,
  },

  computed: {
    allArgs() {
      return {
        ...this.action.args,
        ...this.action.extraArgs.reduce((acc, arg) => {
          acc[arg.name] = arg
          return acc
        }, {}),
      }
    },
  },

  methods: {
    onArgAdd() {
      this.$emit('add')
      this.$nextTick(() => {
        const args = this.$el.querySelectorAll('.action-extra-arg-name')
        if (!args.length)
          return

        args[args.length - 1].focus()
      })
    },

    onArgEdit(name, event) {
      this.$emit('arg-edit', {
        name: name,
        value: event.target?.value || event.detail,
      })
    },

    onExtraArgNameEdit(i, value) {
      this.$emit('extra-arg-name-edit', {
        index: i,
        value: value,
      })
    },

    onExtraArgValueEdit(i, value) {
      this.$emit('extra-arg-value-edit', {
        index: i,
        value: value,
      })
    },

    onSelect(arg) {
      this.$emit('select', arg)
    },

    onKeyDown(event) {
      if (event.key === 'Enter' && !(event.shiftKey || event.ctrlKey || event.altKey || event.metaKey))
        this.onEnter(event)
    },

    onEnter(event) {
      if (!event.target.tagName.match(/input|textarea/i))
        return

      event.preventDefault()
      this.$emit('input', this.allArgs)
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";
</style>
