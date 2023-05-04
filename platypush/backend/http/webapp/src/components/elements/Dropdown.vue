<template>
  <div class="dropdown-container" ref="container">
    <button :title="title" ref="button" @click.stop="toggle($event)">
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

  methods: {
    documentClickHndl(event) {
      if (!this.visible)
        return

      let element = event.target
      while (element) {
        if (!this.$refs.dropdown)
          break
        if (element === this.$refs.dropdown.element)
          return

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

        if (element.getBoundingClientRect().left > window.innerWidth/2)
          element.style.left = (-element.clientWidth + parseFloat(getComputedStyle(this.$refs.button).width)) + 'px'

        if (element.getBoundingClientRect().top > window.innerHeight/2)
          element.style.top = (-element.clientHeight + parseFloat(getComputedStyle(this.$refs.button).height)) + 'px'
      }, 10)
    },

    toggle(event) {
      event.stopPropagation()
      this.$emit('click')
      this.visible ? this.close() : this.open()
    },
  },
}
</script>

<style lang="scss" scoped>
.dropdown-container {
  position: relative;
  display: inline-flex;
  flex-direction: column;

  button {
    background: $default-bg-2;
    border: 0;
    padding: 0.5em;

    &:hover {
      color: $default-hover-fg;
    }
  }

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

:deep(.dropdown-container) {
  button {
    width: 100%;
    height: 100%;
    color: $default-fg-2;
    background: $dropdown-bg;
    border: 0;
    padding: 0.75em 0.5em;
    text-align: left;
    letter-spacing: 0.01em;

    &:hover {
      background: $hover-bg;
      color: $default-fg-2;
    }

    .text {
      padding-left: 0.25em;
    }
  }
}

</style>
