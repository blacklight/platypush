<template>
  <div class="dragged"
       :class="{ hidden: !draggingVisible }"
       :style="{ top: `${top}px`, left: `${left}px` }">
    <div class="content"
         v-html="element?.outerHTML || '...'"
         v-if="draggingVisible" />
  </div>
</template>

<script>
export default {
  emits: [
    'contextmenu',
    'drag',
    'drop',
  ],

  props: {
    disabled: {
      type: Boolean,
      default: false,
    },

    element: {
      type: Object,
    },

    touchDragStartThreshold: {
      type: Number,
      default: 500,
    },

    touchDragMoveCancelDistance: {
      type: Number,
      default: 10,
    },

    value: {
      type: Object,
      default: () => ({}),
    },
  },

  data() {
    return {
      dragging: false,
      draggingHTML: null,
      eventsHandlers: {
        contextmenu: this.onContextMenu,
        drag: this.onDrag,
        dragend: this.onDragEnd,
        dragstart: this.onDragStart,
        drop: this.onDrop,
        touchcancel: this.onDrop,
        touchend: this.onTouchEnd,
        touchmove: this.onTouchMove,
        touchstart: this.onTouchStart,
      },
      initialCursorOffset: null,
      left: 0,
      top: 0,
      touchDragStartTimer: null,
      touchScrollDirection: [0, 0],
      touchScrollSpeed: 10,
      touchScrollTimer: null,
      touchStart: null,
      touchOverElement: null,
    }
  },

  computed: {
    draggingVisible() {
      return this.dragging && this.touchStart
    },

    shouldScroll() {
      return this.touchScrollDirection[0] || this.touchScrollDirection[1]
    },
  },

  methods: {
    onContextMenu(event) {
      // If the element is disabled, or there's no touch start event, then we should
      // emit the contextmenu event as usual.
      if (this.disabled || !this.touchStart) {
        this.$emit('contextmenu', event)
        return
      }

      // Otherwise, if a touch start event was registered, then we should prevent the
      // context menu event from being emitted, as it's most likely a long touch event
      // that should trigger the drag event.
      event.preventDefault()
      event.stopPropagation()
      this.onDragStart(event)
    },

    onDragStart(event) {
      if (this.disabled) {
        return
      }

      this.dragging = true
      this.draggingHTML = this.$slots.default?.()?.el?.outerHTML
      event.value = this.value

      if (event.dataTransfer) {
        event.dataTransfer.dropEffect = 'move'
        event.dataTransfer.effectAllowed = 'move'
        event.dataTransfer.setData('application/json', JSON.stringify(this.value))
      }

      this.cancelTouchDragStart()
      this.$emit('drag', event)
    },

    onDragEnd(event) {
      if (this.disabled) {
        return
      }

      this.reset()
      this.$emit('drop', event)
    },

    onTouchStart(event) {
      if (this.disabled) {
        return
      }

      const touch = event.touches?.[0]
      if (!touch) {
        return
      }

      this.touchStart = [touch.clientX, touch.clientY]
      this.cancelTouchDragStart()
      this.touchDragStartTimer = setTimeout(() => {
        this.onDragStart(event)
      }, this.touchDragStartThreshold)
    },

    onTouchMove(event) {
      if (this.disabled) {
        return
      }

      const touch = event.touches?.[0]
      if (!(touch && this.touchStart)) {
        return
      }

      // If we received a touch move event, and there's a touch drag start timer,
      // then most likely the user is not trying to drag the element, but just scrolling.
      // In this case, we should cancel the drag start timer.
      if (this.touchDragStartTimer) {
        const distance = Math.hypot(
          touch.clientX - this.touchStart[0],
          touch.clientY - this.touchStart[1]
        )

        if (distance > this.touchDragMoveCancelDistance) {
          this.reset()
          return
        }

        this.onDragStart(event)
      }

      event.preventDefault()
      const { clientX, clientY } = touch
      this.left = clientX
      this.top = clientY
      this.left = clientX - this.touchStart[0]
      this.top = clientY - this.touchStart[1]
      this.touchScroll(event)

      // Get droppable element under the touch, excluding the current dragged element
      let droppable = document.elementsFromPoint(clientX, clientY).filter(
        el => el.dataset?.droppable && !el.classList.contains('dragged')
      )?.[0]

      if (!droppable) {
        this.touchOverElement = null
        return
      }

      this.dispatchEvent('dragenter', droppable)
      this.touchOverElement = droppable
    },

    touchScroll(event) {
      if (this.disabled) {
        return
      }

      const parent = this.getScrollableParent()
      if (!parent) {
        return
      }

      const touch = event.touches?.[0]
      if (!touch) {
        return
      }

      const { clientX, clientY } = touch
      const rect = parent.getBoundingClientRect()
      const touchOffset = [
        (clientX - rect.left) / rect.width,
        (clientY - rect.top) / rect.height
      ]

      const scrollDirection = [0, 0]

      if (touchOffset[0] < 0) {
        scrollDirection[0] = -1
      } else if (touchOffset[0] > 1) {
        scrollDirection[0] = 1
      }

      if (touchOffset[1] < 0) {
        scrollDirection[1] = -1
      } else if (touchOffset[1] > 1) {
        scrollDirection[1] = 1
      }

      this.handleTouchScroll(scrollDirection, parent)
    },

    onTouchEnd(event) {
      if (this.disabled) {
        return
      }

      const droppable = this.touchOverElement
      if (droppable) {
        this.dispatchEvent('drop', droppable)
      }

      this.onDragEnd(event)
    },

    onDrop(event) {
      if (this.disabled) {
        return
      }

      this.reset()
      this.$emit('drop', event)
    },

    handleTouchScroll(value, parent) {
      this.touchScrollDirection = value
      if (!(value[0] || value[1])) {
        this.cancelScroll()
        return
      }

      if (this.touchScrollTimer) {
        return
      }

      this.touchScrollTimer = setInterval(() => {
        if (!parent) {
          return
        }

        const [x, y] = value
        parent.scrollBy(x * this.touchScrollSpeed, y * this.touchScrollSpeed)
      }, 1000 / 60)
    },

    getScrollableParent() {
      let parent = this.element?.parentElement
      while (parent) {
        if (
          parent.scrollHeight > parent.clientHeight ||
          parent.scrollWidth > parent.clientWidth
        ) {
          const style = window.getComputedStyle(parent)
          if (['scroll', 'auto'].includes(style.overflowY) || ['scroll', 'auto'].includes(style.overflowX)) {
            return parent
          }
        }

        parent = parent.parentElement
      }
      return null
    },

    dispatchEvent(type, droppable) {
      droppable.dispatchEvent(
        new DragEvent(
          type, {
            target: {
              ...droppable,
              value: this.value,
            }
          }
        )
      )
    },

    cancelScroll() {
      this.touchScrollDirection = [0, 0]

      if (this.touchScrollTimer) {
        clearInterval(this.touchScrollTimer)
        this.touchScrollTimer = null
      }
    },

    cancelTouchDragStart() {
      if (this.touchDragStartTimer) {
        clearTimeout(this.touchDragStartTimer)
        this.touchDragStartTimer = null
      }
    },

    reset() {
      this.cancelTouchDragStart()
      this.cancelScroll()
      this.dragging = false
      this.touchStart = null
      this.touchOverElement = null
      this.left = 0
      this.top = 0
      this.initialCursorOffset = null
    },

    installHandlers() {
      console.debug('Installing drag handlers on', this.element)
      this.element?.setAttribute('draggable', true)
      Object.entries(this.eventsHandlers).forEach(([event, handler]) => {
        this.element?.addEventListener(event, handler)
      })
    },

    uninstallHandlers() {
      console.debug('Uninstalling drag handlers from', this.element)
      this.element?.setAttribute('draggable', false)
      Object.entries(this.eventsHandlers).forEach(([event, handler]) => {
        this.element?.removeEventListener(event, handler)
      })
    },
  },

  watch: {
    dragging() {
      if (this.dragging) {
        this.element?.classList.add('dragged')
        this.$nextTick(() => {
          if (!this.touchStart) {
            return
          }

          this.initialCursorOffset = [
            this.element?.offsetLeft - this.touchStart[0],
            this.element?.offsetTop - this.touchStart[1]
          ]
        })
      } else {
        this.element?.classList.remove('dragged')
      }
    },

    disabled(value) {
      if (value) {
        this.reset()
        this.uninstallHandlers()
      } else {
        this.installHandlers()
      }
    },

    element() {
      this.uninstallHandlers()
      this.installHandlers()
    },

    touchOverElement(value, oldValue) {
      if (value === oldValue) {
        return
      }

      if (oldValue) {
        this.dispatchEvent('dragleave', oldValue)
      }

      if (value) {
        this.dispatchEvent('dragenter', value)
      }
    },
  },

  mounted() {
    this.installHandlers()
  },

  unmounted() {
    this.uninstallHandlers()
  },
}
</script>

<style lang="scss" scoped>
.dragged {
  position: absolute;
  max-width: 100%;
  max-height: 100%;
  transform: scale(0.5);
  z-index: 1000;
}
</style>
