<template>
  <div class="row" :class="classes" :style="style">
    <slot />
  </div>
</template>

<script>
export default {
  name: "Row",
  props: {
    // Class override
    class: {
      type: String,
      required: false,
      default: '',
    },

    // Style override
    style: {
      type: String,
      required: false,
      default: '',
    },
  },

  computed: {
    classes() {
      return this.class
    },
  }
}
</script>

<style scoped>
.row {
  width: 100%;
}
</style>
