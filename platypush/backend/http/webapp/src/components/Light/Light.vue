<template>
  <div class="light">
    {{ light.name || light.id }}
  </div>
</template>

<script>
export default {
  name: "Light",
  props: {
    light: {
      type: Object,
      default: () => {},
    },
  },
}
</script>

<style scoped>

</style>