<template>
  <div class="dropdown-container">
    <button :title="title" ref="button" @click.stop="toggle($event)">
      <i class="icon" :class="iconClass" v-if="iconClass" />
      <span class="text" v-text="text" v-if="text" />
    </button>

    <div class="body-container hidden" ref="dropdownContainer">
      <DropdownBody :id="id" :keepOpenOnItemClick="keepOpenOnItemClick" ref="dropdown">
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
  },

  data() {
    return {
      visible: false,
    }
  },

  computed: {
    dropdownWidth() {
      const dropdown = this.$refs.dropdown?.$el
      if (!dropdown)
        return 0

      return parseFloat(getComputedStyle(dropdown).width)
    },

    dropdownHeight() {
      const dropdown = this.$refs.dropdown?.$el
      if (!dropdown)
        return 0

      return parseFloat(getComputedStyle(dropdown).height)
    },

    buttonStyle() {
      if (!this.$refs.button)
        return {}

      return getComputedStyle(this.$refs.button)
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

    close() {
      this.visible = false
      document.removeEventListener('click', this.documentClickHndl)
      bus.emit('dropdown-close')
    },

    open() {
      document.addEventListener('click', this.documentClickHndl)
      this.visible = true
      this.$refs.dropdownContainer.classList.remove('hidden')
      this.$nextTick(() => {
        const buttonRect = this.$refs.button.getBoundingClientRect()
        const buttonPos = {
          left: buttonRect.left + window.scrollX,
          top: buttonRect.top + window.scrollY,
        }

        const pos = {
          left: buttonPos.left,
          top: buttonPos.top + this.buttonHeight,
        }

        if ((pos.left + this.dropdownWidth) > (window.innerWidth + window.scrollX) / 2) {
          pos.left -= (this.dropdownWidth - this.buttonWidth)
        }

        if ((pos.top + this.dropdownHeight) > (window.innerHeight + window.scrollY) / 2) {
          pos.top -= (this.dropdownHeight + this.buttonHeight - 10)
        }

        const element = this.$refs.dropdown.$el
        element.classList.add('fade-in')
        element.style.top = `${pos.top}px`
        element.style.left = `${pos.left}px`
        bus.emit('dropdown-open', this.$refs.dropdown)
        this.$refs.dropdownContainer.classList.add('hidden')
      })
    },

    toggle(event) {
      event.stopPropagation()
      this.$emit('click')
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
