<template>
  <div class="autocomplete-with-context">
    <Autocomplete
      v-bind="autocompleteProps"
      @blur="onBlur"
      @focus="onFocus"
      @input="onInput"
      @select="onSelect"
      ref="input" />

    <div class="spacer" ref="spacer" />
  </div>
</template>

<script>
import Autocomplete from "@/components/elements/Autocomplete"
import AutocompleteProps from "@/mixins/Autocomplete/Props"

export default {
  emits: ["blur", "focus", "input"],
  components: { Autocomplete },
  mixins: [AutocompleteProps],

  props: {
    quote: {
      type: Boolean,
      default: false,
    },
  },

  computed: {
    autocompleteItemsElement() {
      return this.$refs.input?.$el?.querySelector(".items")
    },

    autocompleteItemsHeight() {
      return this.autocompleteItemsElement?.clientHeight || 0
    },

    autocompleteProps() {
      return {
        ...Object.fromEntries(
          Object.entries(this.$props).filter(([key]) => key !== "quote")
        ),
        items: this.items,
        value: this.value,
        inputOnBlur: false,
        inputOnSelect: false,
        showAllItems: true,
        showResultsWhenBlank: true,
      }
    },

    textInput() {
      return this.$refs.input?.$refs?.input
    },
  },

  methods: {
    emitInput(value) {
      this.$emit(
        "input",
        new CustomEvent("input", {
          detail: value,
          bubbles: true,
          cancelable: true,
        })
      )
    },

    isWithinQuote(selection) {
      let ret = false
      let value = '' + this.value
      selection = [...selection]

      while (selection[0] > 0) {
        if (value[selection[0] - 1] === '$' && value[selection[0]] === '{') {
          ret = true
          break
        }

        selection[0]--
      }

      if (!ret)
        return false

      ret = false
      while (selection[1] < value.length) {
        if (value[selection[1]] === '}') {
          ret = true
          break
        }

        selection[1]++
      }

      return ret
    },

    onBlur(event) {
      this.$emit("blur", event)
      this.$refs.spacer.style.height = "0"
    },

    onFocus(event) {
      this.$emit("focus", event)
      setTimeout(() => {
        this.$refs.spacer.style.height = `${this.autocompleteItemsHeight}px`
      }, 10)
    },

    onInput(event) {
      const selection = this.textSelection()
      this.emitInput(event)
      this.resetSelection(selection)
    },

    onSelect(value) {
      this.$nextTick(() => {
        const selection = this.textSelection()
        value = this.quote && !this.isWithinQuote(selection) ? `\${${value}}` : value
        const newValue = typeof this.value === 'string' ? (
          this.value.slice(0, selection[0]) +
          value +
          this.value.slice(selection[1])
        ) : value

        this.emitInput(newValue)
        this.resetSelection([selection[0] + value.length, selection[0] + value.length])
      })
    },

    resetSelection(selection) {
      setTimeout(() => {
        this.textInput?.focus()
        this.textInput?.setSelectionRange(selection[0], selection[1])
      }, 10)
    },

    textSelection() {
      return [this.textInput?.selectionStart, this.textInput?.selectionEnd]
    },
  },
}
</script>

<style lang="scss">
.autocomplete-with-context {
  .item {
    width: 100%;
    display: flex;
    flex-direction: column;

    @include from($tablet) {
      flex-direction: row;
    }

    .suffix {
      display: flex;
      font-size: 0.9em;
      color: $disabled-fg;

      @include from($tablet) {
        margin-left: auto;
      }
    }
  }
}
</style>
