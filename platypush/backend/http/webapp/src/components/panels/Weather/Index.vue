<template>
  <div class="weather-panel">
    <Loading v-if="loading" />

    <main v-else>
      <div class="controls">
        <form class="location-search" @submit.prevent="search">
          <label>
            <input type="text" v-model="searchQuery" :disabled="searching"
                   placeholder="Search a location, or enter lat,long coordinates" />
          </label>
          <button type="submit" title="Search location" :disabled="searching || !searchQuery?.trim()?.length">
            <i class="fas fa-magnifying-glass" />
          </button>

          <div class="search-results" v-if="searchResults.length">
            <div class="result" v-for="(result, index) in searchResults" :key="index"
                 @click="selectLocation(result)">
              <i class="fas fa-location-dot" />&nbsp;
              <span v-text="result.name" />
            </div>
          </div>
        </form>

        <div class="units-toggle" title="Unit system">
          <button :class="{selected: displayUnits === 'metric'}" @click="setUnits('metric')">
            &deg;C
          </button>
          <button :class="{selected: displayUnits === 'imperial'}" @click="setUnits('imperial')">
            &deg;F
          </button>
        </div>
      </div>

      <div class="selected-location" v-if="location">
        <i class="fas fa-location-dot" />&nbsp;
        <span v-text="location.name" />
        <button class="clear" title="Reset to the default location" @click="clearLocation">
          <i class="fas fa-xmark" />
        </button>
      </div>

      <div class="current-weather">
        <h1>
          <WeatherIcon :weather="weather" :icon-color="iconColor" :size="iconSize"
                       v-if="weather" />
          <span class="temperature" v-if="weather?.temperature != null">
            {{ Math.round(parseFloat(weather.temperature)) + '&deg;' }}
          </span>
        </h1>

        <div class="summary" v-if="weather?.summary" v-text="weather.summary" />

        <div class="details" v-if="weather">
          <div class="detail" v-for="detail in visibleDetails" :key="detail.name" :title="detail.name">
            <div class="name">
              <i :class="detail.icon" />&nbsp;
              <span v-text="detail.name" />
            </div>
            <div class="value" v-text="detail.value" />
          </div>
        </div>
      </div>

      <div class="forecast-container">
        <h2>
          <span class="title">Forecast</span>
          <span class="date-selector">
            <label>
              <input type="date" v-model="selectedDate"
                     :min="minForecastDate" :max="maxForecastDate" />
            </label>
            <button title="Show all dates" v-if="selectedDate" @click="selectedDate = null">
              <i class="fas fa-xmark" />
            </button>
          </span>
        </h2>
        <Forecast :forecast="filteredForecast" />
      </div>
    </main>
  </div>
</template>

<script>
import Utils from "@/Utils";
import Loading from "@/components/Loading";
import Forecast from "@/components/panels/Weather/Forecast";
import WeatherIcon from "@/components/panels/Weather/WeatherIcon";

// Generic weather panel that can be used with any plugin that implements
// the `platypush.plugins.weather.WeatherPlugin` interface - e.g.
// `weather.openweathermap` and `weather.buienradar`.
export default {
  name: "Weather",
  mixins: [Utils],
  components: {Forecast, Loading, WeatherIcon},
  props: {
    // Name of the weather plugin to use - e.g. `weather.openweathermap`
    // or `weather.buienradar`.
    pluginName: {
      type: String,
      required: true,
    },

    // Plugin configuration.
    config: {
      type: Object,
      default: () => {},
    },

    // Icon color theme.
    iconColor: {
      type: String,
      default: 'dark',
    },

    // Size of the current weather icon in pixels.
    iconSize: {
      type: Number,
      default: 100,
    },

    // Refresh interval in seconds.
    refreshSeconds: {
      type: Number,
      default: 900,
    },
  },

  data() {
    return {
      weather: undefined,
      forecast: [],
      loading: false,
      refreshInterval: undefined,
      searchQuery: '',
      searchResults: [],
      searching: false,
      location: null,
      units: null,
      selectedDate: null,
    }
  },

  computed: {
    temperatureUnit() {
      return this.weather?.units === 'imperial' ? '°F' : '°C'
    },

    speedUnit() {
      return this.weather?.units === 'imperial' ? 'mph' : 'km/h'
    },

    details() {
      return [
        {
          name: 'Feels like',
          icon: 'fas fa-temperature-half',
          value: this.weather?.apparent_temperature != null ?
            `${Math.round(parseFloat(this.weather.apparent_temperature))}${this.temperatureUnit}` : null,
        },
        {
          name: 'Humidity',
          icon: 'fas fa-droplet',
          value: this.weather?.humidity != null ? `${this.weather.humidity}%` : null,
        },
        {
          name: 'Pressure',
          icon: 'fas fa-gauge-high',
          value: this.weather?.pressure != null ? `${this.weather.pressure} hPa` : null,
        },
        {
          name: 'Wind',
          icon: 'fas fa-wind',
          value: this.weather?.wind_speed != null ? `${this.formatWindSpeed(this.weather.wind_speed)} ${this.speedUnit}` : null,
        },
        {
          name: 'Wind gust',
          icon: 'fas fa-wind',
          value: this.weather?.wind_gust != null ? `${this.formatWindSpeed(this.weather.wind_gust)} ${this.speedUnit}` : null,
        },
        {
          name: 'Wind direction',
          icon: 'fas fa-compass',
          value: this.weather?.wind_direction != null ? `${this.weather.wind_direction}°` : null,
        },
        {
          name: 'Cloud cover',
          icon: 'fas fa-cloud',
          value: this.weather?.cloud_cover != null ? `${this.weather.cloud_cover}%` : null,
        },
        {
          name: 'Rain chance',
          icon: 'fas fa-cloud-rain',
          value: this.weather?.rain_chance != null ? `${this.weather.rain_chance}%` : null,
        },
        {
          name: 'Precipitation',
          icon: 'fas fa-umbrella',
          value: this.weather?.precip_intensity ?
            `${this.weather.precip_intensity} mm/h${this.weather.precip_type ? ' (' + this.weather.precip_type + ')' : ''}` : null,
        },
        {
          name: 'Visibility',
          icon: 'fas fa-eye',
          value: this.weather?.visibility != null ? `${this.weather.visibility} m` : null,
        },
        {
          name: 'Sunrise',
          icon: 'fas fa-sun',
          value: this.weather?.sunrise != null ? this.formatTime(this.weather.sunrise, false) : null,
        },
        {
          name: 'Sunset',
          icon: 'fas fa-moon',
          value: this.weather?.sunset != null ? this.formatTime(this.weather.sunset, false) : null,
        },
      ]
    },

    visibleDetails() {
      return this.details.filter((detail) => detail.value != null)
    },

    displayUnits() {
      return this.units || this.weather?.units || 'metric'
    },

    forecastDates() {
      return [...new Set(
        this.forecast
            .filter((weather) => weather.time != null)
            .map((weather) => this.toDateString(weather.time))
      )].sort()
    },

    minForecastDate() {
      return this.forecastDates[0]
    },

    maxForecastDate() {
      return this.forecastDates[this.forecastDates.length - 1]
    },

    filteredForecast() {
      if (!this.selectedDate)
        return this.forecast

      return this.forecast.filter(
        (weather) => weather.time != null && this.toDateString(weather.time) === this.selectedDate
      )
    },
  },

  methods: {
    // Wind speeds are reported in m/s if the metric system is used,
    // convert them to km/h for display. Imperial values (mph) are
    // reported as-is.
    formatWindSpeed(speed) {
      speed = parseFloat(speed)
      if (this.weather?.units !== 'imperial')
        speed *= 3.6

      return Math.round(speed * 10) / 10
    },

    // Convert a date/time string to a local YYYY-MM-DD string.
    toDateString(time) {
      return new Date(Date.parse(time)).toLocaleDateString('en-CA')
    },

    weatherArgs() {
      const args = {}
      if (this.location) {
        args.lat = this.location.lat
        args.long = this.location.long
      }

      if (this.units)
        args.units = this.units

      return args
    },

    async refresh() {
      this.loading = true

      try {
        const status = await this.request(`${this.pluginName}.status`, this.weatherArgs())
        if (status?.current)
          this.weather = status.current
        if (status?.forecast)
          this.forecast = status.forecast
      } finally {
        this.loading = false
      }
    },

    async search() {
      const query = this.searchQuery?.trim()
      if (!query?.length)
        return

      // Direct lat,long coordinates
      const coords = query.match(/^(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)$/)
      if (coords) {
        this.selectLocation({
          name: query,
          lat: parseFloat(coords[1]),
          long: parseFloat(coords[2]),
        })

        return
      }

      // Free-text location search
      this.searching = true
      try {
        this.searchResults = await this.request(
          `${this.pluginName}.lookup_location`, {location: query}
        )

        if (!this.searchResults.length)
          this.notify({
            title: 'Location search',
            text: `No results found for "${query}"`,
            warning: true,
          })
      } finally {
        this.searching = false
      }
    },

    selectLocation(location) {
      this.location = location
      this.searchResults = []
      this.searchQuery = ''
      this.refresh()
    },

    clearLocation() {
      this.location = null
      this.searchResults = []
      this.searchQuery = ''
      this.refresh()
    },

    setUnits(units) {
      if (units === this.displayUnits)
        return

      this.units = units
      this.refresh()
    },

    onWeatherChange(event) {
      if (event?.plugin_name !== this.pluginName)
        return

      // Ignore push events if a custom location or unit system is selected -
      // the events refer to the plugin's default configuration.
      if (this.location || this.units)
        return

      this.weather = {...(this.weather || {}), ...event}
    },

    onForecastChange(event) {
      if (event?.plugin_name !== this.pluginName)
        return

      if (this.location || this.units)
        return

      this.forecast = event.forecast || []
    },
  },

  mounted() {
    this.refresh()
    this.subscribe(this.onWeatherChange, `weather-panel-update-${this.pluginName}`,
        'platypush.message.event.weather.NewWeatherConditionEvent')
    this.subscribe(this.onForecastChange, `weather-panel-forecast-${this.pluginName}`,
        'platypush.message.event.weather.NewWeatherForecastEvent')
    this.refreshInterval = setInterval(this.refresh, parseInt((this.refreshSeconds * 1000).toFixed(0)))
  },

  unmounted() {
    this.unsubscribe(`weather-panel-update-${this.pluginName}`)
    this.unsubscribe(`weather-panel-forecast-${this.pluginName}`)
    if (this.refreshInterval)
      clearInterval(this.refreshInterval)
  },
}
</script>

<style lang="scss" scoped>
.weather-panel {
  width: 100%;
  height: 100%;
  overflow: auto;
  display: flex;
  justify-content: center;

  main {
    width: 100%;
    max-width: 800px;
    height: max-content;
    display: flex;
    flex-direction: column;
    background: $background-color;

    @include from($tablet) {
      margin: 1.5em auto;
      border-radius: 1.5em;
      border: $default-border-3;
      box-shadow: $border-shadow-bottom-right;
    }
  }

  .controls {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    padding: 0.75em;
    border-bottom: $default-border-2;

    .location-search {
      position: relative;
      display: flex;
      align-items: center;
      flex-grow: 1;
      max-width: 30em;
      border: none;
      box-shadow: none;
      background: none;
      padding: 0;
      margin: 0;

      label {
        flex-grow: 1;
      }

      input[type=text] {
        width: 100%;
      }

      button {
        margin-left: 0.5em;
        border-radius: 1.5em;
      }

      .search-results {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        z-index: 10;
        max-height: 20em;
        overflow: auto;
        background: $background-color;
        border: $default-border-2;
        border-radius: 0 0 0.75em 0.75em;
        box-shadow: $border-shadow-bottom-right;

        .result {
          padding: 0.5em;
          cursor: pointer;
          border-bottom: $default-border-2;

          &:last-child {
            border-bottom: none;
          }

          &:hover {
            background: $hover-bg;
          }
        }
      }
    }

    .units-toggle {
      display: flex;
      margin-left: 0.75em;

      button {
        padding: 0.4em 0.75em;

        &:first-child {
          border-radius: 1.5em 0 0 1.5em;
        }

        &:last-child {
          border-radius: 0 1.5em 1.5em 0;
        }

        &.selected {
          background: $selected-bg;
          border-color: $default-hover-fg;
        }
      }
    }
  }

  .selected-location {
    display: flex;
    align-items: center;
    padding: 0.5em 0.75em;
    font-size: 0.9em;
    border-bottom: $default-border-2;

    button.clear {
      background: none;
      border: none;
      padding: 0 0.5em;
      margin-left: 0.25em;
      cursor: pointer;

      &:hover {
        color: $default-hover-fg;
      }
    }
  }

  .current-weather {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1em;
    border-bottom: $default-border-2;

    h1 {
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .temperature {
      font-size: 2em;
      margin-left: 0.4em;
    }

    .summary {
      font-size: 1.1em;
      margin-top: 0.75em;
    }

    .details {
      width: 100%;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      margin-top: 1.5em;

      .detail {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 0.5em 1em;

        .name {
          font-size: 0.85em;
          opacity: 0.7;
        }

        .value {
          font-size: 1.1em;
        }
      }
    }
  }

  .forecast-container {
    display: flex;
    flex-direction: column;

    h2 {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 1.2em;
      padding: 0.5em;
      border-bottom: $default-border-2;

      .date-selector {
        display: flex;
        align-items: center;
        font-size: 0.8em;
        font-weight: normal;

        button {
          background: none;
          border: none;
          padding: 0 0.5em;
          cursor: pointer;

          &:hover {
            color: $default-hover-fg;
          }
        }
      }
    }
  }
}
</style>
