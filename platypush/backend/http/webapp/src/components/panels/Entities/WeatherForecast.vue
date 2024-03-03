<template>
  <div class="entity weather-forecast-container">
    <div class="head">
      <div class="col-1 icon">
        <WeatherIcon :value="firstForecast" v-if="firstForecast" />
        <EntityIcon
          :entity="value"
          :loading="loading"
          :error="error"
          v-else />
      </div>

      <div class="col-5 name" @click.stop="isCollapsed = !isCollapsed">
        <div class="name" v-text="value.name" />
      </div>

      <div class="col-5 summary-container" @click.stop="isCollapsed = !isCollapsed">
        <div class="summary">
          <span class="temperature"
                v-text="normTemperature"
                v-if="normTemperature != null" />
        </div>
      </div>

      <div class="col-1 collapse-toggler" @click.stop="isCollapsed = !isCollapsed">
        <i class="fas"
          :class="{'fa-chevron-down': isCollapsed, 'fa-chevron-up': !isCollapsed}" />
      </div>
    </div>

    <div class="body children attributes fade-in" v-if="!isCollapsed">
      <div class="child" v-for="weather in value.forecast" :key="weather.time">
        <Weather :value="weather" :is-forecast="true" />
      </div>
    </div>
  </div>
</template>

<script>
import EntityIcon from "./EntityIcon"
import EntityMixin from "./EntityMixin"
import Weather from "./Weather"
import WeatherIcon from "./WeatherIcon"

export default {
  components: {EntityIcon, Weather, WeatherIcon},
  mixins: [EntityMixin],

  data() {
    return {
      isCollapsed: true,
    }
  },

  computed: {
    firstForecast() {
      return this.value?.forecast?.[0]
    },

    normTemperature() {
      if (this.firstForecast?.temperature == null)
        return null

      return Math.round(this.firstForecast.temperature).toFixed(1) + "°"
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.weather-forecast-container {
  .body {
    padding-top: 0;
    max-height: 35em;
    overflow-y: auto;

    .child {
      padding: 0;
      margin: 0 -0.5em;

      &:hover {
        background: $hover-bg !important;
        cursor: pointer;
      }
    }
  }

  .summary-container {
    display: flex;
    align-items: center;
    font-size: 1.25em;

    .summary {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      flex-grow: 1;
      margin-right: 0.5em;
    }

    .temperature {
      margin-left: 0.5em;
    }
  }
}
</style>
