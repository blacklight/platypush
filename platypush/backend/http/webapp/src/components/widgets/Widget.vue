<template>
  <div :style="style" :class="classes">
    <slot />
  </div>
</template>

<script>
export default {
  name: "Widget",
  props: {
    // Widget style override
    style: {
      type: String,
      required: false,
      default: '',
    },

    // Widget class override
    class: {
      type: String,
      required: false,
      default: '',
    },
  },

  computed: {
    classes() {
      return (this.class && this.class.length ? this.class.split(' ') : ['col-3']).concat(['widget', 'column'])
    },
  },
}
</script>

<style lang="scss" scoped>
.widget {
  height: calc(100% - 1em);
  background: $background-color;
  border-radius: 5px;
  display: flex;
  justify-content: center;
  align-content: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 3px 3px 0 rgba(0,0,0,0.16), 0 0 0 1px rgba(0,0,0,0.08);
}
</style>
