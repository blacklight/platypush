<template>
  <div class="entity weather-container">
    <div class="head">
      <div class="col-1 icon">
        <EntityIcon
          :entity="value"
          :loading="loading"
          :error="error" />
      </div>

      <div class="col-5 name">
        <div class="name" v-text="value.name" />
      </div>

      <div class="col-5 current-weather" @click.stop="isCollapsed = !isCollapsed">
        <div class="weather-summary">
          <img :src="`/icons/openweathermap/dark/${value.icon}.png`"
               :alt="value?.summary"
               class="weather-icon"
               v-if="value.icon" />

          <img :src="value.image"
               :alt="value?.summary"
               class="weather-icon"
               v-else-if="value.image" />

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
      <div class="child" v-if="value.summary">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Summary</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.summary" />
        </div>
      </div>

      <div class="child" v-if="value.temperature">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Temperature</div>
        </div>
        <div class="value">
          <div class="name" v-text="normTemperature" />
        </div>
      </div>

      <div class="child" v-if="normApparentTemperature">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Feels Like</div>
        </div>
        <div class="value">
          <div class="name" v-text="normApparentTemperature" />
        </div>
      </div>

      <div class="child" v-if="value.humidity">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Humidity</div>
        </div>
        <div class="value">
          <div class="name" v-text="normPercentage(value.humidity)" />
        </div>
      </div>

      <div class="child" v-if="normPrecipIntensity && precipIconClass">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Precipitation</div>
        </div>
        <div class="value">
          <div class="name">
            <i :class="precipIconClass" /> &nbsp;
            <span v-text="normPrecipIntensity" />
          </div>
        </div>
      </div>

      <div class="child" v-if="value.cloud_cover">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Cloud Cover</div>
        </div>
        <div class="value">
          <div class="name" v-text="normPercentage(value.cloud_cover)" />
        </div>
      </div>

      <div class="child" v-if="normPressure">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Pressure</div>
        </div>
        <div class="value">
          <div class="name" v-text="normPressure" />
        </div>
      </div>

      <div class="child" v-if="value.rain_chance != null">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Rain Chance</div>
        </div>
        <div class="value">
          <div class="name" v-text="normPercentage(value.rain_chance)" />
        </div>
      </div>

      <div class="child" v-if="value.wind_speed != null">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Wind</div>
        </div>
        <div class="value">
          <div class="name">
            <span v-text="value.wind_speed" />
            <span v-if="isMetric">m/s</span>
            <span v-else>mph</span>
          </div>
        </div>
      </div>

      <div class="child" v-if="value.wind_gust != null">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Wind Gust</div>
        </div>
        <div class="value">
          <div class="name">
            <span v-text="value.wind_gust" />
            <span v-if="isMetric">m/s</span>
            <span v-else>mph</span>
          </div>
        </div>
      </div>

      <div class="child" v-if="value.wind_direction != null">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Wind Direction</div>
        </div>
        <div class="value">
          <span class="name" v-text="value.wind_direction" />&deg;
        </div>
      </div>

      <div class="child" v-if="value.visibility != null">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Visibility</div>
        </div>
        <div class="value">
          <div class="name">
            <span v-text="value.visibility" />
            <span v-if="isMetric">m</span>
            <span v-else>mi</span>
          </div>
        </div>
      </div>

      <div class="child" v-if="value.sunrise != null">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Sunrise</div>
        </div>
        <div class="value">
          <div class="name" v-text="formatDateTime(value.sunrise)" />
        </div>
      </div>

      <div class="child" v-if="value.sunset != null">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Sunset</div>
        </div>
        <div class="value">
          <div class="name" v-text="formatDateTime(value.sunset)" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EntityIcon from "./EntityIcon"
import EntityMixin from "./EntityMixin"

export default {
  components: {EntityIcon},
  mixins: [EntityMixin],

  data() {
    return {
      isCollapsed: true,
    }
  },

  computed: {
    normTemperature() {
      if (this.value.temperature == null)
        return null

      return Math.round(this.value.temperature).toFixed(1) + "°"
    },

    normApparentTemperature() {
      if (this.value.apparent_temperature == null)
        return null

      return Math.round(this.value.apparent_temperature).toFixed(1) + "°"
    },

    normPrecipIntensity() {
      if (!this.value.precip_intensity)
        return null

      return (
        Math.round(this.value.precip_intensity).toFixed(1) +
        (this.isMetric ? "mm" : "in") + "/h"
      )
    },

    normPressure() {
      if (this.value.pressure == null)
        return null

      return Math.round(this.value.pressure) + "hPa"
    },

    precipIconClass() {
      if (this.value.precip_type == null)
        return null

      switch (this.value.precip_type.toLowerCase()) {
        case "rain":
          return "fas fa-cloud-rain"
        case "snow":
          return "fas fa-snowflake"
        case "sleet":
          return "fa-cloud-meatball"
        default:
          return null
      }
    },

    isMetric() {
      return this.value.units === "metric"
    },
  },

  methods: {
    normPercentage(value) {
      if (value == null)
        return null

      return Math.round(value) + "%"
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.weather-container {
  .current-weather {
    display: flex;
    align-items: center;
    font-size: 1.25em;

    .weather-summary {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      flex-grow: 1;
      margin-right: 0.5em;
    }

    .weather-icon {
      max-width: 100%;
      max-height: 100%;
      width: 1.5em;
      height: 1.5em;
    }

    .temperature {
      margin-left: 0.5em;
    }
  }
}
</style>
