<template>
  <div class="modal-container fade-in" :id="id" :class="{hidden: !isVisible}" :style="{'--z-index': zIndex}" @click="close">
    <div class="modal">
      <div class="content" :style="{'--width': width, '--height': height}" @click="$event.stopPropagation()">
        <div class="header" v-text="title" v-if="title"></div>
        <div class="body">
          <slot @modal-close="close" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
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
  },

  data() {
    return {
      timeoutId: undefined,
      prevVisible: this.visible,
      isVisible: this.visible,
    }
  },

  computed: {
    zIndex() {
      return 500 + this.level
    },
  },

  methods: {
    close() {
      this.prevVisible = this.isVisible
      this.isVisible = false
    },

    show() {
      this.prevVisible = this.isVisible
      this.isVisible = true
    },

    toggle() {
      if (this.isVisible)
        this.close()
      else
        this.show()
    },
  },

  mounted() {
    const self = this
    const visibleHndl = (visible) => {
      if (!visible)
        self.$emit('close')
      else
        self.$emit('open')
    }

    this.$watch(() => this.visible, visibleHndl)
    this.$watch(() => this.isVisible, visibleHndl)
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
      border-bottom: $modal-header-border;
      border-radius: 0.5em 0.5em 0 0;
      padding: 0.5em;
      text-align: center;
      justify-content: center;
      align-items: center;
      background: $modal-header-bg;
      text-transform: uppercase;
    }

    .body {
      max-height: 75vh;
      overflow: auto;
      padding: 2em;
    }
  }
}
</style>