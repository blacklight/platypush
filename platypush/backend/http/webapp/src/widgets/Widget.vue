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
      let classes = ['widget', 'column']
      if (this.class && this.class.length)
        classes = classes.concat(this.class.split(' '))
      else
        classes = classes.concat('col-3')

      return classes
    },
  },
}
</script>

<style lang="scss" scoped>
.widget {
  background: $background-color;
  border-radius: 5px;
  margin-bottom: 1em;
  display: flex;
  justify-content: center;
  align-content: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 3px 3px 0 rgba(0,0,0,0.16), 0 0 0 1px rgba(0,0,0,0.08);
}

@media screen and (max-width: $tablet){
  .widget {
    height: calc(100% - 1em);
  }
}

@media screen and (min-width: $desktop){
  .widget {
    height: calc(50% - 1em);
  }
}
</style>