<template>
  <span class="entity weather-icon-container">
    <img :src="`/icons/openweathermap/dark/${value.icon}.png`"
         :alt="value?.summary"
         class="weather-icon"
         v-if="value.icon" />

    <img :src="value.image"
         :alt="value?.summary"
         class="weather-icon"
         v-else-if="value.image" />
  </span>
</template>

<script>
export default {
  props: {
    value: Object,
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.weather-icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 2.5em;

  .weather-icon {
    max-width: 100%;
    height: 100%;
    margin: 0.5em 0.5em 0.5em 1em;
  }
}
</style>
