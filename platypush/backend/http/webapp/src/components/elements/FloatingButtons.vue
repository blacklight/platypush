<template>
  <div class="floating-btns" :class="{direction: direction}">
    <slot />
  </div>
</template>

<script>
export default {
  emits: ["click"],
  props: {
    direction: {
      type: String,
      default: "row",
    },

    size: {
      type: String,
      default: "4em",
    },
  },

  computed: {
    buttons() {
      return this.$el.querySelectorAll(".floating-btn")
    },
  },

  mounted() {
    const buttons = Array.from(this.buttons)
    let offset = 0
    buttons.forEach((button, index) => {
      const size = button.offsetWidth
      const styleOffset = `calc(${offset}px + (${index} * 1em))`
      if (this.direction === "row") {
        if (!parseFloat(getComputedStyle(button).left))
          button.style.left = styleOffset
        else
          button.style.right = styleOffset
      } else {
        if (!parseFloat(getComputedStyle(button).top))
          button.style.top = styleOffset
        else
          button.style.bottom = styleOffset
      }

      offset += size
    })
  },
}
</script>
