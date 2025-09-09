<template>
  <div class="autocomplete" :class="{ 'with-items': showItems }">
    <label :text="label">
      <input
        type="text"
        class="input"
        ref="input" 
        :placeholder="placeholder"
        :disabled="disabled"
        :value="value"
        @focus.stop="onFocus"
        @input.stop="onInput"
        @blur="onBlur"
        @keydown="onInputKeyDown"
        @keyup="onInputKeyUp"
       >
    </label>

    <div class="items" ref="items" v-if="showItems">
      <div
        class="item"
        :class="{ active: i === curIndex }"
        :key="getItemText(item)"
        :data-item="getItemText(item)"
        v-for="(item, i) in visibleItems"
        @click.stop="onItemSelect(item)">
        <span class="prefix" v-html="item.prefix" v-if="item.prefix"></span>
        <span class="matching" v-if="value?.length">{{ getItemText(item).substr(0, value.length) }}</span>
        <span class="normal">{{ getItemText(item).substr(value?.length || 0) }}</span>
        <span class="suffix" v-html="item.suffix" v-if="item.suffix"></span>
      </div>
    </div>
  </div>
</template>

<script>
import Props from "@/mixins/Autocomplete/Props"

export default {
  emits: ["blur", "focus", "input", "select"],
  mixins: [Props],

  data() {
    return {
      visible: false,
      curIndex: null,
      selectItemTimer: null,
    }
  },

  computed: {
    itemsText() {
      return this.items.map((item) => this.getItemText(item))
    },

    visibleItems() {
      if (!this.value?.length || this.showAllItems)
        return this.items

      const val = this.value.toUpperCase()
      if (!val?.length)
        return this.showResultsWhenBlank ? this.items : []

      return this.items.filter(
        (item) => this.getItemText(item).substr(0, val.length).toUpperCase() === val
      )
    },

    showItems() {
      return this.visible && this.items?.length
    },
  },

  methods: {
    getItemText(item) {
      return item?.text || item
    },

    valueIsInItems() {
      if (this.showAllItems)
        return true

      if (!this.value)
        return false

      return this.itemsText.indexOf(this.value) >= 0
    },

    onFocus(e) {
      this.$emit("focus", e)
      if (this.showResultsWhenBlank || this.value?.length)
        this.visible = true
    },

    onInput(e) {
      let val = e.target?.value
      if (val == null) {
        e.stopPropagation?.()
        return
      }

      if (this.valueIsInItems())
        this.visible = false

      e.stopPropagation()
      this.$emit("input", val.text || val)
      this.curIndex = null
      this.visible = true
    },

    onBlur(e) {
      if (this.inputOnBlur) {
        this.onInput(e)
        this.$nextTick(() => {
          if (this.valueIsInItems()) {
            this.visible = false
          }
        })

        return
      }

      e.stopPropagation()

      if (this.keepFocus)
        this.$nextTick(() => this.$refs.input.focus())

      setTimeout(() => {
        if (this.selectItemTimer) {
          this.$nextTick(() => this.$refs.input.focus())
          return
        }

        this.$emit("blur", e)
        if (this.valueIsInItems()) {
          this.visible = false
        }
      }, 200)
    },

    onItemSelect(item) {
      if (this.selectItemTimer) {
        clearTimeout(this.selectItemTimer)
        this.selectItemTimer = null
      }

      this.selectItemTimer = setTimeout(() => {
        this.selectItemTimer = null
      }, 250)

      const text = item.text || item
      this.$emit("select", text)
      if (this.inputOnSelect)
        this.$emit("input", text)

      this.$nextTick(() => {
        if (this.valueIsInItems()) {
          if (this.inputOnSelect) {
            this.visible = false
          } else {
            this.visible = true
            this.curIndex = this.visibleItems.indexOf(item)
            if (this.curIndex < 0)
              this.curIndex = null

            this.$refs.input.focus()
          }
        }
      })
    },

    onInputKeyUp(e) {
      if (
        ["ArrowUp", "ArrowDown", "Escape"].indexOf(e.key) >= 0 ||
        (e.key === "Tab" && this.selectOnTab) ||
        (e.key === "Enter" && this.curIndex != null)
      ) {
        e.stopPropagation()
      }

      if (e.key === "Enter" && this.valueIsInItems() && this.curIndex != null) {
        this.$refs.input.blur()
        this.visible = false
      }
    },

    onInputKeyDown(e) {
      if (!this.showItems)
        return

      if (
        e.key === 'ArrowDown' ||
        (e.key === 'Tab' && !e.shiftKey && this.selectOnTab) ||
        (e.key === 'j' && e.ctrlKey)
      ) {
        e.stopPropagation()
        this.curIndex = this.curIndex == null ? 0 : this.curIndex + 1
        e.preventDefault()
      } else if (
        e.key === 'ArrowUp' ||
        (e.key === 'Tab' && e.shiftKey && this.selectOnTab) ||
        (e.key === 'k' && e.ctrlKey)
      ) {
        e.stopPropagation()
        this.curIndex = this.curIndex == null ? this.visibleItems.length - 1 : this.curIndex - 1
        e.preventDefault()
      } else if (e.key === 'Enter') {
        // Only intercept if we actually have a highlighted item to select.
        if (this.curIndex != null && this.curIndex >= 0 && this.visible) {
          e.preventDefault()
          e.stopPropagation()
          this.onItemSelect(this.visibleItems[this.curIndex])
          this.$nextTick(() => this.$refs.input.focus())
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

  watch: {
    curIndex() {
      // Do nothing if the index is not set
      if (this.curIndex == null)
        return

      // Go to the beginning after reaching the end
      if (this.curIndex >= this.visibleItems.length)
        this.curIndex = 0

      // Go to the end after moving back from the start
      if (this.curIndex < 0)
        this.curIndex = this.visibleItems.length - 1

      // Scroll to the element
      const curText = this.getItemText(this.visibleItems[this.curIndex])
      const el = this.$el.querySelector(`[data-item='${curText}']`)
      if (el) {
        el.scrollIntoView({
          block: "start",
          inline: "nearest",
          behavior: "smooth",
        })
      }
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
