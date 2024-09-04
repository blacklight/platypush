<template>
  <div class="droppable" />
</template>

<script>
export default {
  emits: [
    'dragenter',
    'dragleave',
    'dragover',
    'drop',
  ],

  props: {
    element: {
      type: Object,
    },

    active: {
      type: Boolean,
      default: false,
    },

    disabled: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      eventsHandlers: {
        dragenter: this.onDragEnter,
        dragleave: this.onDragLeave,
        dragover: this.onDragOver,
        drop: this.onDrop,
      },
      selected: false,
    }
  },

  methods: {
    onDragEnter(event) {
      if (this.disabled || this.selected) {
        return
      }

      this.selected = true
      this.$emit('dragenter', event)
    },

    onDragLeave(event) {
      if (this.disabled || !this.selected) {
        return
      }

      const rect = this.element.getBoundingClientRect()
      if (
        event.clientX >= rect.left &&
        event.clientX <= rect.right &&
        event.clientY >= rect.top &&
        event.clientY <= rect.bottom
      ) {
        return
      }

      this.selected = false
      this.$emit('dragleave', event)
    },

    onDragOver(event) {
      if (this.disabled) {
        return
      }

      event.preventDefault()
      this.selected = true
      this.$emit('dragover', event)
    },

    onDrop(event) {
      if (this.disabled) {
        return
      }

      this.selected = false
      this.$emit('drop', event)
    },

    installHandlers() {
      const el = this.element
      if (!el) {
        return
      }

      console.debug('Installing drop handlers on', this.element)
      if (el.dataset) {
        el.dataset.droppable = true;
      }

      if (el.addEventListener) {
        Object.entries(this.eventsHandlers).forEach(([event, handler]) => {
          el.addEventListener(event, handler)
        })
      }
    },

    uninstallHandlers() {
      const el = this.element
      if (!el) {
        return
      }

      console.debug('Uninstalling drop handlers from', this.element)
      if (el.dataset?.droppable) {
        delete el.dataset.droppable;
      }

      if (el.removeEventListener) {
        Object.entries(this.eventsHandlers).forEach(([event, handler]) => {
          el.removeEventListener(event, handler)
        })
      }
    },
  },

  watch: {
    active() {
      if (this.active) {
        this.element?.classList.add('active')
      } else {
        this.element?.classList.remove('active')
      }
    },

    disabled: {
      handler() {
        if (this.disabled) {
          this.element?.classList.add('disabled')
        } else {
          this.element?.classList.remove('disabled')
        }
      },
    },

    element: {
      handler() {
        this.uninstallHandlers()
        this.installHandlers()
      },
    },

    selected: {
      handler(value, oldValue) {
        if (value && !oldValue) {
          this.element?.classList.add('selected')
        } else if (!value && oldValue) {
          this.element?.classList.remove('selected')
        }
      },
    },
  },

  mounted() {
    this.$nextTick(() => {
      this.installHandlers()
    })
  },

  unmounted() {
    this.uninstallHandlers()
  },
}
</script>
