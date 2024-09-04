<template>
  <div class="modal-container fade-in"
       :class="{hidden: !isVisible}"
       :id="id"
       :style="{'--z-index': zIndex}" 
       ref="container"
       @click.stop="close">
    <div class="modal" :class="$attrs.class" ref="modal">
      <div class="content" :style="{'--width': width, '--height': height}" @click.stop>
        <div class="header" :class="{uppercase: uppercase}" v-if="title">
          <div class="title" v-text="title" v-if="title" />
          <div class="buttons">
            <button v-for="(button, index) in buttons"
                    :key="index"
                    :title="button.title"
                    @click.stop="button.action">
              <i :class="button.icon" />
            </button>

            <button title="Close" alt="Close" @click.stop="close">
              <i class="fas fa-xmark" />
            </button>
          </div>
        </div>
        <div class="body">
          <slot @modal-close="close" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { bus } from "@/bus";

export default {
  name: "Modal",
  emits: ['close', 'open'],
  props: {
    // Modal ID
    id: {
      type: String,
    },

    // Modal title
    title: {
      type: String,
    },

    // Modal width
    width: {
      type: [Number, String],
    },

    // Modal height
    height: {
      type: [Number, String],
    },

    // Modal initial visibility value
    visible: {
      type: Boolean,
      default: false,
    },

    // Modal timeout in seconds
    timeout: {
      type: [Number, String],
    },

    // Modal z-index level
    level: {
      type: Number,
      default: 1,
    },

    // Whether the header title should be uppercase
    uppercase: {
      type: Boolean,
      default: true,
    },

    // Extra buttons to be added to the modal header
    buttons: {
      type: Array,
      default: () => [],
    },

    // A function to be called before the modal is closed.
    // If the function returns false, the modal will not be closed.
    beforeClose: {
      type: Function,
      default: () => true,
    },
  },

  data() {
    return {
      ignoreEscape: false,
      isVisible: this.visible,
      prevVisible: this.visible,
      timeoutId: undefined,
    }
  },

  computed: {
    zIndex() {
      return 500 + this.level
    },
  },

  methods: {
    close(event) {
      if (this.beforeClose && !this.beforeClose())
        return

      if (event)
        event.preventDefault()

      this.prevVisible = this.isVisible
      this.isVisible = false
      bus.emit('modal-close')
    },

    hide() {
      this.close()
    },

    show() {
      this.prevVisible = this.isVisible
      this.isVisible = true
    },

    open() {
      this.show()
    },

    toggle() {
      if (this.isVisible)
        this.close()
      else
        this.show()
    },

    onEscape() {
      if (!this.isVisible || this.ignoreEscape)
        return

      const myZIndex = parseInt(getComputedStyle(this.$refs.container).zIndex)
      const maxZIndex = Math.max(
        ...Array.from(
          document.querySelectorAll('.modal-container:not(.hidden)')
        ).map((modal) =>
          parseInt(getComputedStyle(modal).zIndex)
        )
      )

      // Close only if it's the outermost modal
      if (myZIndex === maxZIndex)
        this.close()
    },

    onKeyUp(event) {
      event.stopPropagation()
      if (event.key === 'Escape') {
        this.onEscape()
      }
    },

    onModalCloseMessage() {
      if (!this.isVisible)
        return

      this.ignoreEscape = true
      setTimeout(() => this.ignoreEscape = false, 100)
    },

    visibleHndl(visible) {
      if (!visible)
        this.$emit('close')
      else
        this.$emit('open')
    },
  },

  watch: {
    visible(value) {
      this.visibleHndl(value)
      this.isVisible = value
    },

    isVisible(value) {
      this.visibleHndl(value)
    },
  },

  mounted() {
    document.body.addEventListener('keyup', this.onKeyUp)
    bus.on('modal-close', this.onModalCloseMessage)
  },

  unmounted() {
    document.body.removeEventListener('keyup', this.onKeyUp)
  },

  updated() {
    this.prevVisible = this.isVisible
    if (this.isVisible) {
      // Make sure that a newly opened or visible+updated modal always comes to the front
      let maxZIndex = parseInt(getComputedStyle(this.$el).zIndex)
      let outermostModals = []

      for (const modal of document.querySelectorAll('.modal-container:not(.hidden)')) {
        const zIndex = parseInt(getComputedStyle(modal).zIndex)

        if (zIndex > maxZIndex) {
          maxZIndex = zIndex
          outermostModals = [modal]
        } else if (zIndex === maxZIndex) {
          outermostModals.push(modal)
        }
      }

      if (outermostModals.indexOf(this.$el) < 0 || outermostModals.length > 1) {
        this.$el.style.zIndex = maxZIndex+1
      }
    }

    if (this.isVisible && this.timeout && !this.timeoutId) {
      const handler = (self) => {
        return () => {
          // self.modalClose()
          self.close()
          self.timeoutId = undefined
        }
      }

      this.timeoutId = setTimeout(handler(this), 0+this.timeout)
    }
  },
}
</script>

<style lang="scss" scoped>
$icon-size: 1.5em;
$icon-margin: 0.5em;

.modal-container {
  position: fixed;
  display: flex;
  align-items: center;
  justify-content: center;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: var(--z-index);
  background: rgba(10,10,10,0.9);

  .modal {
    display: flex;
    max-width: 100%;
    justify-content: center;

    .content {
      --width: auto;
      --height: auto;
      width: var(--width);
      height: var(--height);
      border-radius: 0.5em;
      background: $modal-body-bg;
    }

    .header {
      display: flex;
      position: relative;
      border-bottom: $modal-header-border;
      border-radius: 0.5em 0.5em 0 0;
      padding: 0.5em;
      text-align: center;
      justify-content: center;
      align-items: center;
      background: $modal-header-bg;

      &.uppercase {
        text-transform: uppercase;
      }

      .buttons {
        width: auto;
        position: absolute;
        right: 0;
      }

      button {
        width: $icon-size;
        height: $icon-size;
        margin: auto $icon-margin;
        padding: 0;
        border: 0;
        background: transparent;

        &:hover {
          color: $default-hover-fg;
        }
      }
    }

    .body {
      max-height: 75vh;
      overflow: auto;
      padding: 2em;
    }
  }
}
</style>
