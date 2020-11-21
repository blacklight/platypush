<template>
  <div class="date-time-weather">
    <div class="date" v-text="formatDate(now)"></div>
    <div class="time" v-text="formatTime(now)"></div>

    <h1 class="weather">
      <skycons :condition="weatherIcon" :paused="animPaused" :size="iconSize" v-if="weatherIcon" />
      <span class="temperature" v-if="weather">
        {{ Math.round(parseFloat(weather.temperature)) + '&deg;' }}
      </span>
    </h1>

    <div class="summary" v-if="weather && weather.summary" v-text="weather.summary"></div>

    <div class="sensors" v-if="Object.keys(sensors).length">
      <div class="sensor temperature col-6" v-if="sensors.temperature">
        <i class="fas fa-thermometer-half"></i> &nbsp;
        <span class="temperature">
          {{ parseFloat(sensors.temperature).toFixed(1) + '&deg;' }}
        </span>
      </div>

      <div class="sensor humidity col-6" v-if="sensors.humidity">
        <i class="fa fa-tint"></i> &nbsp;
        <span class="humidity">
          {{ parseFloat(sensors.humidity).toFixed(1) + '%' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";
import Skycons from "vue-skycons"

// Widget to show date, time, weather and temperature information
export default {
  name: 'DateTimeWeather',
  mixins: [Utils],
  components: {Skycons},
  props: {
    // If false then the weather icon will be animated.
    // Otherwise, it will be a static image.
    paused: {
      type: Boolean,
      required: false,
      default: false,
    },

    // Size of the weather icon in pixels
    iconSize: {
      type: Number,
      required: false,
      default: 50,
    },
  },

  computed: {
    animPaused() {
      return !!parseInt(this.paused)
    },
  },

  data: function() {
    return {
      weather: undefined,
      sensors: {},
      now: new Date(),
      weatherIcon: undefined,
    };
  },

  methods: {
    async refresh() {
      const weather = (await this.request('weather.darksky.get_hourly_forecast')).data[0]
      this.onWeatherChange(weather)
    },

    refreshTime() {
      this.now = new Date()
    },

    formatDate(date) {
      return date.toDateString().substring(0, 10)
    },

    formatTime(date) {
      return date.toTimeString().substring(0, 8)
    },

    onWeatherChange(event) {
      if (!this.weather)
        this.weather = {}

      this.weather = {...this.weather, ...event}
      this.weatherIcon = this.weather.icon
    },

    onSensorData(event) {
      if ('temperature' in event.data)
        this.sensors.temperature = event.data.temperature

      if ('humidity' in event.data)
        this.sensors.temperature = event.data.humidity
    },
  },

  mounted: function() {
    this.refresh()
    setInterval(this.refresh, 900000)
    setInterval(this.refreshTime, 1000)

    // TODO
    // registerEventHandler(this.onWeatherChange, 'platypush.message.event.weather.NewWeatherConditionEvent')
    // registerEventHandler(this.onSensorData, 'platypush.message.event.sensor.SensorDataChangeEvent')
  },
}
</script>

<style lang="scss" scoped>
.date-time-weather {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 0.1em;

  .date {
    font-size: 1.3em;
    height: 10%;
  }

  .time {
    font-size: 2em;
    height: 14%;
  }

  .weather {
    height: 25%;
    display: flex;
    align-items: center;
    margin-top: 15%;

    .temperature {
      font-size: 3.1em;
      margin-left: 0.4em;
    }
  }

  .summary {
    height: 28%;
  }

  .sensors {
    width: 100%;
    height: 13%;

    .sensor {
      padding: 0 0.1em;
    }

    .humidity {
      text-align: right;
    }
  }
}
</style>
