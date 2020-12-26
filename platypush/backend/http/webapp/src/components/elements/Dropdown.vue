<template>
  <div class="dropdown-container" ref="container">
    <button :title="title" ref="button" @click.stop="toggle">
      <i class="icon" :class="iconClass" v-if="iconClass" />
      <span class="text" v-text="text" v-if="text" />
    </button>

    <div class="dropdown fade-in" :id="id" :class="{hidden: !visible}" ref="dropdown">
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  name: "Dropdown",
  emits: ['click'],
  props: {
    id: {
      type: String,
    },

    items: {
      type: Array,
      default: () => [],
    },

    iconClass: {
      type: String,
    },

    text: {
      type: String,
    },

    title: {
      type: String,
    },
  },

  data() {
    return {
      visible: false,
    }
  },

  methods: {
    documentClickHndl(event) {
      if (!this.visible)
        return

      let element = event.target
      while (element) {
        if (element === this.$refs.dropdown.element) {
          return
        }

        element = element.parentElement
      }

      this.close()
    },

    close() {
      this.visible = false
      document.removeEventListener('click', this.documentClickHndl)
    },

    open() {
      document.addEventListener('click', this.documentClickHndl)
      this.visible = true

      setTimeout(() => {
        const element = this.$refs.dropdown
        element.style.left = 0
        element.style.top = parseFloat(getComputedStyle(this.$refs.button).height) + 'px'

        const maxOffset = 45
        const maxLeft = window.innerWidth - maxOffset
        const left = this.$refs.container.offsetLeft + element.offsetLeft
        const width = element.clientWidth

        if (left + width >= maxLeft) {
          element.style.left = -(parseFloat(getComputedStyle(this.$refs.button).width) + maxOffset) + 'px'
        }
      }, 10)
    },

    toggle() {
      this.visible ? this.close() : this.open()
    },
  },
}
</script>

<style lang="scss" scoped>
.dropdown-container {
  position: relative;
  display: flex;
  flex-direction: column;

  .dropdown {
    position: absolute;
    width: max-content;
    background: $dropdown-bg;
    border-radius: .25em;
    border: $default-border-3;
    box-shadow: $dropdown-shadow;
    display: flex;
    flex-direction: column;
    z-index: 1;
  }
}
</style>
