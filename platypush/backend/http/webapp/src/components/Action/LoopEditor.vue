<template>
  <form class="loop-editor" @submit.prevent.stop="onSubmit">
    for
    <label for="iterator">
      <input type="text"
             name="iterator"
             autocomplete="off"
             :autofocus="true"
             placeholder="Iterator"
             :value="iterator"
             ref="iterator"
             @input.stop="onInput('iterator', $event)" />
    </label>

    in

    <label for="iterable">
      <input type="text"
             name="iterable"
             autocomplete="off"
             :autofocus="true"
             placeholder="Iterable"
             :value="iterable"
             ref="iterable"
             @input.stop="onInput('iterable', $event)" />
    </label>

    <label class="async">
      <input class="checkbox"
             type="checkbox"
             name="async"
             :checked="async"
             @input.stop="onInput('async', $event)" />&nbsp;
        Run in parallel
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
    'change',
    'input',
  ],

  props: {
    async: {
      type: Boolean,
      default: false,
    },

    iterable: {
      type: String,
      default: '',
    },

    iterator: {
      type: String,
      default: '',
    },
  },

  data() {
    return {
      hasChanges: true,
    }
  },

  methods: {
    onSubmit() {
      const iterator = this.$refs.iterator.value.trim()
      const iterable = this.$refs.iterable.value.trim()
      if (!iterator.length || !iterable.length) {
        return
      }

      this.$emit('change', { iterator, iterable })
    },

    onInput(target, event) {
      const value = '' + event.target.value
      if (!value?.trim()?.length) {
        this.hasChanges = false
      } else {
        if (target === 'iterator') {
          this.hasChanges = value !== this.iterator
        }

        if (!this.hasChanges && target === 'iterable') {
          this.hasChanges = value !== this.iterable
        }

        if (!this.hasChanges && target === 'async') {
          this.hasChanges = value !== this.async
        }
      }

      this.$nextTick(() => {
        event.target.value = value
      })
    },
  },

  watch: {
    value() {
      this.hasChanges = false
    },
  },

  mounted() {
    this.$nextTick(() => {
      this.$refs.iterator.focus()
    })
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.loop-editor {
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

    &.async {
      justify-content: flex-start;
      padding-bottom: 0;
    }
  }
}
</style>
