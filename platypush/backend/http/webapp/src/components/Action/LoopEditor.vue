<template>
  <form class="loop-editor" @submit.prevent.stop="onSubmit">
    for
    <label for="iterator">
      <input type="text"
             name="iterator"
             autocomplete="off"
             :autofocus="true"
             placeholder="Iterator"
             :value="newValue.iterator"
             ref="iterator"
             @input.stop="onInput('iterator', $event)" />
    </label>

    in

    <label for="iterable">
      <ContextAutocomplete :value="newValue.iterable"
                           :items="contextAutocompleteItems"
                           placeholder="Iterable"
                           @input.stop="onInput('iterable', $event)"
                           ref="iterable" />

    </label>

    <label class="async">
      <input class="checkbox"
             type="checkbox"
             name="async"
             ref="async"
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
import ContextAutocomplete from "./ContextAutocomplete"
import Mixin from "./Mixin"

export default {
  emits: ['change', 'input'],
  mixins: [Mixin],
  components: { ContextAutocomplete },
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
      newValue: {
        iterator: null,
        iterable: null,
        async: null,
      },
    }
  },

  methods: {
    onSubmit() {
      const iterator = this.$refs.iterator.value.trim()
      const iterable = this.$refs.iterable.value.trim()
      const async_ = this.$refs.async.checked
      if (!iterator.length || !iterable.length) {
        return
      }

      this.$emit('change', { iterator, iterable, async: async_ })
    },

    onInput(target, event) {
      const value = '' + (event.target?.value || event.detail)
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
        this.newValue[target] = value
      })
    },
  },

  watch: {
    value() {
      this.hasChanges = false
      this.newValue = {
        iterator: this.iterator,
        iterable: this.iterable,
        async: this.async,
      }
    },
  },

  mounted() {
    this.newValue = {
      iterator: this.iterator,
      iterable: this.iterable,
      async: this.async,
    }

    this.$nextTick(() => {
      this.$refs.iterator.focus()
    })
  },
}
</script>

<style lang="scss" scoped>
@import "common";

@mixin label {
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;

  input[type="text"] {
    width: 100%;
    margin-left: 1em;
  }

  &.async {
    justify-content: flex-start;
    padding-bottom: 0;
  }
}

.loop-editor {
  min-width: 40em;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;

  label {
    @include label;
    padding: 1em;
  }
}

:deep(label) {
  @include label;

  .autocomplete-with-context,
  .autocomplete {
    width: 100%;
  }
}
</style>
