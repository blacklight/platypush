<template>
  <div class="forecast">
    <div class="no-items" v-if="!forecast?.length">
      No forecast data available
    </div>

    <div class="forecast-item" v-for="(weather, index) in forecast" :key="index">
      <div class="time col-3">
        {{ formatDateTime(weather.time, false, false) }}
      </div>

      <div class="icon col-2">
        <WeatherIcon :weather="weather" :size="iconSize" />
      </div>

      <div class="temperature col-2">
        {{ formatTemperature(weather) }}
      </div>

      <div class="summary col-5" v-text="weather.summary" />
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";
import WeatherIcon from "@/components/panels/Weather/WeatherIcon";

// Shared component to display a list of weather forecast items,
// regardless of the underlying weather plugin.
export default {
  name: "Forecast",
  mixins: [Utils],
  components: {WeatherIcon},
  props: {
    // List of forecast items, as returned by the `get_forecast` action
    // or attached to a `NewWeatherForecastEvent`.
    forecast: {
      type: Array,
      default: () => [],
    },

    // Size of the weather icons in pixels.
    iconSize: {
      type: Number,
      default: 40,
    },
  },

  methods: {
    formatTemperature(weather) {
      if (weather?.temperature == null)
        return 'N/A'

      return Math.round(parseFloat(weather.temperature)) + '°'
    },
  },
}
</script>

<style lang="scss" scoped>
.forecast {
  width: 100%;
  display: flex;
  flex-direction: column;

  .no-items {
    padding: 2em;
    font-size: 1.2em;
    display: flex;
    justify-content: center;
  }

  .forecast-item {
    width: 100%;
    display: flex;
    align-items: center;
    padding: 0.25em 0.5em;
    border-bottom: $default-border-2;

    &:hover {
      background: $hover-bg;
    }

    .time {
      font-size: 0.9em;
      opacity: 0.8;
    }

    .icon {
      display: flex;
      justify-content: center;
    }

    .temperature {
      font-size: 1.2em;
      display: flex;
      justify-content: center;
    }

    .summary {
      text-overflow: ellipsis;
      overflow: hidden;
      white-space: nowrap;
    }
  }
}
</style>
