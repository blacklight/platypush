<template>
  <div class="date-time-weather">
    <div class="row date-time-container">
      <DateTime :show-date="_showDate" :show-time="_showTime" :show-seconds="_showSeconds" :animate="animate"
                v-if="_showDate || _showTime" />
    </div>

    <div class="row weather-container">
      <Weather :show-summary="_showSummary" :animate="_animate" :icon-size="iconSize"
               :refresh-seconds="weatherRefreshSeconds" v-if="showWeather"/>
    </div>

    <div class="row sensors-container">
      <div class="row" v-if="_showSensors && Object.keys(sensors).length">
        <div class="col-3">
          <Sensor icon-class="fas fa-thermometer-half" :value="sensors.temperature" unit="°"
                  v-if="typeof sensors.temperature === 'number'" />
        </div>

        <div class="col-6">&nbsp;</div>

        <div class="col-3">
          <Sensor icon-class="fas fa-tint" :value="sensors.humidity" unit="%"
                  v-if="typeof sensors.humidity === 'number'" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";
import DateTime from "@/components/widgets/DateTime/Index";
import Weather from "@/components/widgets/Weather/Index";
import Sensor from "@/components/Sensor";

// Widget to show date, time, weather and temperature information
export default {
  name: 'DateTimeWeather',
  mixins: [Utils],
  components: {Sensor, DateTime, Weather},
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

    // If false then don't display the date.
    showDate: {
      required: false,
      default: true,
    },

    // If false then don't display the time.
    showTime: {
      required: false,
      default: true,
    },

    // If false then don't display the weather.
    showWeather: {
      required: false,
      default: true,
    },

    // If false then the weather summary won't be displayed.
    showSummary: {
      required: false,
      default: true,
    },

    // If false then temperature/humidity sensor data won't be shown.
    showSensors: {
      required: false,
      default: true,
    },

    // If false then don't display the seconds.
    showSeconds: {
      required: false,
      default: true,
    },

    // Name of the attribute on a received SensorDataChangeEvent that
    // represents the temperature value to be rendered.
    sensorTemperatureAttr: {
      type: String,
      required: false,
      default: 'temperature',
    },

    // Name of the attribute on a received SensorDataChangeEvent that
    // represents the humidity value to be rendered.
    sensorHumidityAttr: {
      type: String,
      required: false,
      default: 'humidity',
    },

    // Weather refresh interval in seconds.
    weatherRefreshSeconds: {
      type: Number,
      required: false,
      default: 900,
    },
  },

  computed: {
    _showDate() {
      return this.parseBoolean(this.showDate)
    },

    _showTime() {
      return this.parseBoolean(this.showTime)
    },

    _showSeconds() {
      return this.parseBoolean(this.showSeconds)
    },

    _showWeather() {
      return this.parseBoolean(this.showWeather)
    },

    _showSummary() {
      return this.parseBoolean(this.showSummary)
    },

    _showSensors() {
      return this.parseBoolean(this.showSensors)
    },

    _animate() {
      return this.parseBoolean(this.animate)
    },
  },

  data: function() {
    return {
      sensors: {},
    };
  },

  methods: {
    onSensorData(event) {
      if (this.sensorTemperatureAttr in event.data)
        this.sensors.temperature = event.data.temperature

      if (this.sensorHumidityAttr in event.data)
        this.sensors.humidity = event.data.humidity
    },
  },

  mounted() {
    this.subscribe(this.onSensorData, null, 'platypush.message.event.sensor.SensorDataChangeEvent');
  },
}
</script>

<style lang="scss" scoped>
.date-time-weather {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 0.5em;

  .row {
    text-align: center;
  }

  .date-time-container {
    height: 35%;
  }

  .weather-container {
    height: 45%;
  }

  .sensors-container {
    width: 100%;
    height: 20%;
    position: relative;

    .row {
      width: 100%;
      position: absolute;
      bottom: 0;
    }
  }
}
</style>
