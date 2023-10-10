<template>
  <div class="autocomplete">
    <label :text="label">
      <input
        type="text"
        class="input"
        ref="input" 
        :placeholder="placeholder"
        :disabled="disabled"
        :value="value"
        @focus="onFocus"
        @input="onInput"
        @blur="onInput"
        @keydown="onInputKeyDown"
        @keyup="onInputKeyUp"
       >
    </label>

    <div class="items" v-if="showItems">
      <div
        class="item"
        :class="{ active: i === curIndex }"
        :key="item"
        :data-item="item"
        v-for="(item, i) in visibleItems"
        @click="onItemSelect(item)"
      >
        <span class="matching">{{ item.substr(0, value.length) }}</span>
        <span class="normal">{{ item.substr(value.length) }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Autocomplete",
  emits: ["input"],
  props: {
    items: {
      type: Array,
      required: true,
    },

    value: {
      type: String,
      default: "",
    },

    disabled: {
      type: Boolean,
      default: false,
    },

    autofocus: {
      type: Boolean,
      default: false,
    },

    label: {
      type: String,
    },

    placeholder: {
      type: String,
    },

    showResultsWhenBlank: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      visible: false,
      curIndex: -1,
    }
  },

  computed: {
    visibleItems() {
      const val = this.value.toUpperCase()
      if (!val?.length)
        return this.showResultsWhenBlank ? this.items : []

      return this.items.filter(
        (item) => item.substr(0, val.length).toUpperCase() === val
      )
    },

    showItems() {
      return this.visible && this.items?.length
    },
  },

  methods: {
    selectNextItem() {
      this.curIndex++
      this.normalizeIndex()
    },

    selectPrevItem() {
      this.curIndex--
      this.normalizeIndex()
    },

    normalizeIndex() {
      // Go to the beginning after reaching the end
      if (this.curIndex >= this.visibleItems.length)
        this.curIndex = 0

      // Go to the end after moving back from the start
      if (this.curIndex < 0)
        this.curIndex = this.visibleItems.length - 1

      // Scroll to the element
      const el = this.$el.querySelector("[data-item='" + this.visibleItems[this.curIndex] + "']")
      if (el)
        el.scrollIntoView({
          block: "start",
          inline: "nearest",
          behavior: "smooth",
        })
    },

    valueIsInItems() {
      return this.items.indexOf(this.value) >= 0
    },

    onFocus() {
      if (this.showResultsWhenBlank || this.value?.length)
        this.visible = true
    },

    onInput(e) {
      let val = e.target.value
      if (this.valueIsInItems())
        this.visible = false

      e.stopPropagation()
      this.$emit("input", val)
      this.curIndex = -1
      this.visible = true
    },

    onItemSelect(item) {
      this.$emit("input", item)
      this.$nextTick(() => {
        if (this.valueIsInItems()) {
          this.visible = false
        }
      })
    },

    onInputKeyUp(e) {
      if (["ArrowUp", "ArrowDown", "Tab", "Enter", "Escape"].indexOf(e.key) >= 0)
        e.stopPropagation()

      if (e.key === "Enter" && this.valueIsInItems()) {
        this.$refs.input.blur()
        this.visible = false
      }
    },

    onInputKeyDown(e) {
      if (
        e.key === 'ArrowDown' ||
        (e.key === 'Tab' && !e.shiftKey) ||
        (e.key === 'j' && e.ctrlKey)
      ) {
        this.selectNextItem()
        e.preventDefault()
      } else if (
        e.key === 'ArrowUp' ||
        (e.key === 'Tab' && e.shiftKey) ||
        (e.key === 'k' && e.ctrlKey)
      ) {
        this.selectPrevItem()
        e.preventDefault()
      } else if (e.key === 'Enter') {
        if (this.curIndex > -1 && this.visible) {
          e.preventDefault()
          this.onItemSelect(this.visibleItems[this.curIndex])
          this.$refs.input.focus()
        }
      } else if (e.key === 'Escape') {
        this.visible = false
      }
    },

    onDocumentClick(e) {
      if (this.$el.contains(e.target) || e.target.classList.contains("item"))
        return

      this.visible = false
    },
  },

  mounted() {
    document.addEventListener("click", this.onDocumentClick)
    if (this.autofocus)
      this.$refs.input.focus()
  },
}
</script>

<style lang="scss" scoped>
.autocomplete {
  width: 100%;
  position: relative;
  display: inline-block;

  .input {
    width: 100%;
    box-shadow: $search-bar-shadow;
  }

  .items {
    width: 100%;
    max-height: 50vh;
    position: absolute;
    overflow: auto;
    border: $default-border-2;
    border-bottom: none;
    border-top: none;
    border-radius: 1em;
    box-shadow: $search-bar-shadow;
    z-index: 99;
    top: 100%;
    left: 0;
    right: 0;

    .item {
      padding: 1em;
      cursor: pointer;
      border-bottom: $default-border-2;
      background-color: $background-color;

      &:hover {
        background-color: $hover-bg-2;
      }

      .matching {
        font-weight: bold;
      }
    }
  }

  .active {
    background-color: $hover-bg-2 !important;
  }
}
</style>
