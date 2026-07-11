<template>
  <Weather plugin-name="weather.buienradar" :config="config" />
</template>

<script>
import Weather from "@/components/panels/Weather/Index";

export default {
  name: "WeatherBuienradar",
  components: {Weather},
  props: {
    config: {
      type: Object,
      default: () => {},
    },
  },
}
</script>
