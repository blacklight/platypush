<template>
  <form class="expression-editor" @submit.prevent.stop="onSubmit">
    <label for="expression">
      <slot />

      <ContextAutocomplete :value="newValue"
                           :items="contextAutocompleteItems"
                           :quote="quote"
                           @input.stop="onInput"
                           ref="input" />
    </label>

    <label>
      <button type="submit" :disabled="!hasChanges">
        <i class="fas fa-check" />&nbsp;Save
      </button>
    </label>
  </form>
</template>

<script>
import ContextAutocomplete from "./ContextAutocomplete"
import Mixin from "./Mixin"

export default {
  emits: ['input'],
  mixins: [Mixin],
  components: { ContextAutocomplete },

  props: {
    value: {
      type: [String, Number, Boolean, Object, Array],
      default: '',
    },

    allowEmpty: {
      type: Boolean,
      default: false,
    },

    placeholder: {
      type: String,
      default: '',
    },

    quote: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      hasChanges: false,
      newValue: null,
    }
  },

  methods: {
    onSubmit(event) {
      const value = this.newValue?.trim()
      if (!value.length && !this.allowEmpty) {
        return
      }

      event.target.value = value
      this.$emit('input', event)
    },

    onInput(event) {
      if (event?.detail == null)
        return

      const value = '' + event.detail
      if (!value?.trim()?.length) {
        this.hasChanges = this.allowEmpty
      } else {
        this.hasChanges = value !== this.value
      }

      this.$nextTick(() => {
        this.newValue = value
      })
    },
  },

  watch: {
    value() {
      this.hasChanges = false
    },
  },

  mounted() {
    this.hasChanges = false
    this.newValue = this.value

    if (!this.value?.trim?.()?.length) {
      this.hasChanges = this.allowEmpty
    }

    this.$nextTick(() => {
      this.textInput?.focus()
    })
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.expression-editor {
  min-width: 40em;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;

  label {
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 1em;

    input[type="text"] {
      width: 100%;
      margin-left: 1em;
    }
  }
}
</style>
