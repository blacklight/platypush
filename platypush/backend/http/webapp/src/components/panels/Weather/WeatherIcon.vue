<template>
  <img :src="iconUrl" :alt="weather?.summary" :width="size" :height="size"
       class="weather-icon" v-if="iconUrl" />
</template>

<script>
// Shared weather icon component.
// It supports both plugins that report a full image URL for the current
// weather condition (e.g. weather.buienradar, through the `image` attribute)
// and plugins that report an icon identifier that should be mapped to a local
// icon (e.g. weather.openweathermap, through the `icon` attribute).
export default {
  name: "WeatherIcon",
  props: {
    // Weather data, as returned by the `get_current_weather` action or
    // attached to a `NewWeatherConditionEvent`.
    weather: {
      type: Object,
      required: true,
    },

    // Icon color theme (only applies to icon identifiers, not to image URLs).
    iconColor: {
      type: String,
      default: 'dark',
    },

    // Size of the icon in pixels.
    size: {
      type: Number,
      default: 75,
    },
  },

  computed: {
    iconUrl() {
      if (this.weather?.image)
        return this.weather.image

      if (this.weather?.icon)
        return `/icons/openweathermap/${this.iconColor || 'dark'}/${this.weather.icon}.png`

      return null
    },
  },
}
</script>

<style lang="scss" scoped>
.weather-icon {
  object-fit: contain;
}
</style>
