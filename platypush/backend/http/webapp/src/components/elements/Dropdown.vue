<template>
  <div class="dropdown-container">
    <button :title="title" ref="button" @click.stop="toggle($event)">
      <i class="icon" :class="iconClass" v-if="iconClass" />
      <span class="text" v-text="text" v-if="text" />
    </button>

    <div class="body-container" :class="{ hidden: !visible }" ref="dropdownContainer">
      <DropdownBody :id="id"
                    :keepOpenOnItemClick="keepOpenOnItemClick"
                    :style="style"
                    ref="dropdown"
                    @click="onClick">
        <slot />
      </DropdownBody>
    </div>
  </div>
</template>

<script>
import DropdownBody from "./DropdownBody";
import { bus } from "@/bus";

export default {
  components: { DropdownBody },
  emits: ['click'],
  props: {
    id: {
      type: String,
    },

    iconClass: {
      default: 'fa fa-ellipsis-h',
    },

    text: {
      type: String,
    },

    title: {
      type: String,
    },

    keepOpenOnItemClick: {
      type: Boolean,
      default: false,
    },

    style: {
      type: Object,
      default: () => ({}),
    },
  },

  data() {
    return {
      visible: false,
    }
  },

  computed: {
    button() {
      const el = this.$refs.button?.$el
      if (!el)
        return this.$refs.button

      return el.querySelector('button')
    },

    buttonStyle() {
      if (!this.button)
        return {}

      return getComputedStyle(this.button)
    },

    buttonWidth() {
      return parseFloat(this.buttonStyle.width || 0)
    },

    buttonHeight() {
      return parseFloat(this.buttonStyle.height || 0)
    },
  },

  methods: {
    documentClickHndl(event) {
      if (!this.visible)
        return

      let element = event.target
      while (element) {
        if (element.classList.contains('dropdown'))
          return

        element = element.parentElement
      }

      this.close()
    },

    getDropdownWidth() {
      const dropdown = this.$refs.dropdown?.$el
      if (!dropdown)
        return 0

      return parseFloat(getComputedStyle(dropdown).width)
    },

    getDropdownHeight() {
      const dropdown = this.$refs.dropdown?.$el
      if (!dropdown)
        return 0

      return parseFloat(getComputedStyle(dropdown).height)
    },

    onClick(event) {
      if (!this.keepOpenOnItemClick)
        this.close()

      if (event.target.tagName === 'A') {
        event.preventDefault()
        return false
      }

      if (event.defaultPrevented) {
        event.stopPropagation()
        return false
      }
    },

    close() {
      this.visible = false
      document.removeEventListener('click', this.documentClickHndl)
      bus.emit('dropdown-close')
    },

    open() {
      document.addEventListener('click', this.documentClickHndl)
      const element = this.$refs.dropdown?.$el
      if (!element.parentElement)
        this.$el.appendChild(element)

      this.visible = true
      this.$nextTick(this.adjustDropdownPos)
    },

    adjustDropdownPos() {
      const buttonRect = this.button.getBoundingClientRect()
      const buttonPos = {
        left: buttonRect.left + window.scrollX,
        top: buttonRect.top + window.scrollY,
      }

      const pos = {
        left: buttonPos.left,
        top: buttonPos.top + this.buttonHeight,
      }

      const dropdownWidth = this.getDropdownWidth()
      const dropdownHeight = this.getDropdownHeight()

      if ((pos.left + dropdownWidth) > (window.innerWidth + window.scrollX) / 2) {
        pos.left -= (dropdownWidth - this.buttonWidth)
      }

      if ((pos.top + dropdownHeight) > (window.innerHeight + window.scrollY) / 2) {
        let newPosTop = pos.top - (dropdownHeight + this.buttonHeight - 10)
        if (newPosTop < 0)
          newPosTop = 0

        pos.top = newPosTop
      }

      const element = this.$refs.dropdown.$el
      element.classList.add('fade-in')
      element.style.top = `${pos.top}px`
      element.style.left = `${pos.left}px`
      bus.emit('dropdown-open', this.$refs.dropdown)
    },

    toggle(event) {
      event?.stopPropagation()
      this.$emit('click', event)
      this.visible ? this.close() : this.open()
    },

    onKeyUp(event) {
      event.stopPropagation()
      if (event.key === 'Escape') {
        this.close()
      }
    },
  },

  mounted() {
    document.body.addEventListener('keyup', this.onKeyUp)
  },

  unmounted() {
    document.body.removeEventListener('keyup', this.onKeyUp)
  },
}
</script>

<style lang="scss" scoped>
.dropdown-container {
  position: relative;
  display: inline-flex;
  flex-direction: column;

  button {
    background: none;
    border: 0;
    padding: 0.5em;

    &:hover {
      color: $default-hover-fg;
    }
  }
}
</style>
