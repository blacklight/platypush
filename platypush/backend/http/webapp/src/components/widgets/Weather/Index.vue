<template>
  <div class="weather">
    <Loading v-if="loading" />

    <h1 v-else>
      <skycons :condition="weatherIcon" :paused="!animate" :size="iconSize" :color="iconColor"
               v-if="_showIcon && weatherIcon" />
      <span class="temperature" v-if="_showTemperature && weather">
        {{ Math.round(parseFloat(weather.temperature)) + '&deg;' }}
      </span>
    </h1>

    <div class="summary" v-if="_showSummary && weather && weather.summary" v-text="weather.summary"></div>
  </div>
</template>

<script>
import Utils from "@/Utils";
import Skycons from "vue-skycons"
import Loading from "@/components/Loading";

// Widget to show date, time, weather and temperature information
export default {
  name: 'Weather',
  mixins: [Utils],
  components: {Loading, Skycons},
  props: {
    // If false then the weather icon will be animated.
    // Otherwise, it will be a static image.
    animate: {
      required: false,
      default: true,
    },

    // Size of the weather icon in pixels.
    iconSize: {
      type: Number,
      required: false,
      default: 50,
    },

    // Icon color.
    iconColor: {
      type: String,
      required: false,
    },

    // If false then the weather icon won't be displayed.
    showIcon: {
      required: false,
      default: true,
    },

    // If false then the weather summary won't be displayed.
    showSummary: {
      required: false,
      default: true,
    },

    // If false then the temperature won't be displayed.
    showTemperature: {
      required: false,
      default: true,
    },

    // Refresh interval in seconds.
    refreshSeconds: {
      type: Number,
      required: false,
      default: 900,
    },
  },

  data: function() {
    return {
      weather: undefined,
      weatherIcon: undefined,
      loading: false,
    };
  },

  computed: {
    _showSummary() {
      return this.parseBoolean(this.showSummary)
    },

    _showIcon() {
      return this.parseBoolean(this.showIcon)
    },

    _showTemperature() {
      return this.parseBoolean(this.showTemperature)
    },
  },

  methods: {
    async refresh() {
      this.loading = true

      try {
        const weather = (await this.request('weather.darksky.get_hourly_forecast')).data[0]
        this.onWeatherChange(weather)
      } finally {
        this.loading = false
      }
    },

    onWeatherChange(event) {
      if (!this.weather)
        this.weather = {}

      this.weather = {...this.weather, ...event}
      this.weatherIcon = this.weather.icon
    },
  },

  mounted: function() {
    this.refresh()
    this.subscribe(this.onWeatherChange, null, 'platypush.message.event.weather.NewWeatherConditionEvent')
    setInterval(this.refresh, parseInt((this.refreshSeconds*1000).toFixed(0)))
  },
}
</script>

<style lang="scss" scoped>
.weather {
  display: flex;
  flex-direction: column;

  h1 {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .temperature {
    font-size: 3.1em;
    margin-left: 0.4em;
  }
}
</style>
