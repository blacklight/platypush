<template>
  <div class="args-body">
    <div class="args-list"
         v-if="Object.keys(action.args).length || action.supportsExtraArgs">
      <!-- Supported action arguments -->
      <div class="arg" :key="name" v-for="name in Object.keys(action.args)">
        <label>
          <input type="text"
                 class="action-arg-value"
                 :class="{required: action.args[name].required}"
                 :disabled="running"
                 :placeholder="name"
                 :value="action.args[name].value"
                 @input="onArgEdit(name, $event)"
                 @focus="onSelect(name)">
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
            <input type="text"
                   class="action-extra-arg-value"
                   placeholder="Value"
                   :disabled="running"
                   :value="arg.value"
                   @input="onExtraArgValueEdit(i, $event.target.value)">
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

export default {
  name: 'ActionArgs',
  components: { Argdoc },
  emits: [
    'add',
    'arg-edit',
    'extra-arg-name-edit',
    'extra-arg-value-edit',
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
        value: event.target.value,
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
  },
}
</script>

<style lang="scss" scoped>
@import "common";
</style>
