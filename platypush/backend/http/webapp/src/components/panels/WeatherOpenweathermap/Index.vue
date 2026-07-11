<template>
  <Weather plugin-name="weather.openweathermap" :config="config" />
</template>

<script>
import Weather from "@/components/panels/Weather/Index";

export default {
  name: "WeatherOpenweathermap",
  components: {Weather},
  props: {
    config: {
      type: Object,
      default: () => {},
    },
  },
}
</script>
