<template>
  <form class="expression-editor" @submit.prevent.stop="onSubmit">
    <label for="expression">
      <slot />

      <input type="text"
             name="expression"
             autocomplete="off"
             :autofocus="true"
             :placeholder="placeholder"
             :value="value"
             ref="text"
             @input.stop="onInput" />
    </label>

    <label>
      <button type="submit" :disabled="!hasChanges">
        <i class="fas fa-check" />&nbsp;Save
      </button>
    </label>
  </form>
</template>

<script>
export default {
  emits: [
    'input',
  ],

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
  },

  data() {
    return {
      hasChanges: false,
    }
  },

  methods: {
    onSubmit(event) {
      const value = this.$refs.text.value.trim()
      if (!value.length && !this.allowEmpty) {
        return
      }

      event.target.value = value
      this.$emit('input', event)
    },

    onInput(event) {
      const value = '' + event.target.value
      if (!value?.trim()?.length) {
        this.hasChanges = this.allowEmpty
      } else {
        this.hasChanges = value !== this.value
      }

      this.$nextTick(() => {
        this.$refs.text.value = value
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
    if (!this.value?.trim?.()?.length) {
      this.hasChanges = this.allowEmpty
    }

    this.$nextTick(() => {
      this.$refs.text.focus()
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
    flex-direction: row;
    align-items: center;
    justify-content: center;
    padding: 1em;

    input[type="text"] {
      width: 100%;
      margin-left: 1em;
    }
  }
}
</style>
