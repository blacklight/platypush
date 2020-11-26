<template>
  <div class="image-carousel">
    <Loading v-if="!images.length" />
    <div ref="background" class="background" />
    <img ref="img" :src="imgURL" alt="Your carousel images"
         :style="{display: !images.length ? 'none' : 'block'}">

    <div class="row info-container" v-if="_showDate || _showTime">
      <div class="col-6 weather-container">
        <span v-if="!_showWeather">&nbsp;</span>
        <Weather :show-icon="_showWeatherIcon" :show-summary="_showWeatherSummary" :show-temperature="_showTemperature"
                 :icon-color="weatherIconColor" :icon-size="weatherIconSize" :animate="_animateWeatherIcon" v-else />
      </div>

      <div class="col-6 date-time-container">
        <DateTime :show-date="_showDate" :show-time="_showTime" :show-seconds="_showSeconds"
                  v-if="_showTime || _showDate" />
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";
import Loading from "@/components/Loading";
import DateTime from "@/components/widgets/DateTime/Index";
import Weather from "@/components/widgets/Weather/Index";

export default {
  name: "ImageCarousel",
  components: {Weather, DateTime, Loading},
  mixins: [Utils],
  props: {
    // Images directory
    imgDir: {
      type: String,
      required: true,
    },

    // Refresh interval in seconds.
    refreshSeconds: {
      type: Number,
      required: false,
      default: 15,
    },

    // Show the current date on top of the images
    showDate: {
      type: Boolean,
      required: false,
      default: false,
    },

    // Show the current time on top of the images
    showTime: {
      type: Boolean,
      required: false,
      default: false,
    },

    // If false then don't display the seconds.
    showSeconds: {
      type: Boolean,
      required: false,
      default: false,
    },

    // If false then don't display weather info.
    showWeather: {
      type: Boolean,
      required: false,
      default: false,
    },

    // If false then temperature won't be displayed.
    showTemperature: {
      type: Boolean,
      required: false,
      default: true,
    },

    // If false then don't display the weather state icon.
    showWeatherIcon: {
      type: Boolean,
      required: false,
      default: true,
    },

    // If false then don't display the weather summary text.
    showWeatherSummary: {
      type: Boolean,
      required: false,
      default: true,
    },

    // Weather con color.
    weatherIconColor: {
      type: String,
      required: false,
      default: 'white',
    },

    // Size of the weather icon in pixels.
    weatherIconSize: {
      type: Number,
      required: false,
      default: 40,
    },

    // If false then the weather icon will be animated.
    // Otherwise, it will be a static image.
    animateWeatherIcon: {
      required: false,
      default: true,
    },
  },

  data() {
    return {
      images: [],
      currentImage: undefined,
      loading: false,
    }
  },

  computed: {
    imgURL() {
      let port = 8008
      if ('backend.http' in this.$root.config && 'port' in this.$root.config['backend.http']) {
        port = this.$root.config['backend.http'].port
      }

      return '//' + window.location.hostname + ':' + port + this.currentImage
    },

    _showDate() {
      return this.parseBoolean(this.showDate)
    },

    _showTime() {
      return this.parseBoolean(this.showTime)
    },

    _showSeconds() {
      return this.parseBoolean(this.showSeconds)
    },

    _showTemperature() {
      return this.parseBoolean(this.showTemperature)
    },

    _showWeather() {
      return this.parseBoolean(this.showWeather)
    },

    _showWeatherIcon() {
      return this.parseBoolean(this.showWeatherIcon)
    },

    _showWeatherSummary() {
      return this.parseBoolean(this.showWeatherSummary)
    },

    _animateWeatherIcon() {
      return this.parseBoolean(this.animateWeatherIcon)
    }
  },

  methods: {
    async refresh() {
      if (!this.images.length) {
        this.loading = true

        try {
          this.images = await this.request('utils.search_web_directory', {
            directory: this.imgDir,
            extensions: ['.jpg', '.jpeg', '.png'],
          })

          this.shuffleImages()
        } finally {
          this.loading = false
        }
      }

      if (this.images.length) {
        this.currentImage = this.images.pop()
      }
    },

    onNewImage() {
      if (!this.$refs.img)
        return

      this.$refs.background.style['background-image'] = 'url(' + this.imgURL + ')'
      this.$refs.img.style.width = 'auto'

      if (this.$refs.img.width > this.$refs.img.height) {
        const ratio = this.$refs.img.width / this.$refs.img.height
        if (4/3 <= ratio <= 16/9) {
          this.$refs.img.style.width = '100%'
        }

        if (ratio <= 4/3) {
          this.$refs.img.style.height = '100%'
        }
      }
    },

    shuffleImages() {
      for (let i=this.images.length-1; i > 0; i--) {
        let j = Math.floor(Math.random() * (i+1))
        let x = this.images[i]
        this.images[i] = this.images[j]
        this.images[j] = x
      }
    },
  },

  mounted() {
    this.$refs.img.addEventListener('load', this.onNewImage)
    this.$refs.img.addEventListener('error', this.refresh)

    this.refresh()
    setInterval(this.refresh, Math.round(this.refreshSeconds * 1000))
  },
}
</script>

<style lang="scss" scoped>
.image-carousel {
  width: calc(100% + 1.5em);
  height: calc(100% + 1.5em);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: black;
  margin: -0.75em 0.75em 0.75em -0.75em !important;

  .background {
    position: absolute;
    top: 0;
    width: 100%;
    height: 100vh;
    background-color: black;
    background-position: center;
    background-size: cover;
    background-repeat: no-repeat;
    filter: blur(13px);
    -webkit-filter: blur(13px);
  }

  img {
    position: absolute;
    max-height: 100%;
    z-index: 2;
  }
}

.info-container {
  width: 100%;
  position: absolute;
  bottom: 0;
  display: flex;
  align-items: flex-end;
  z-index: 10;
  color: white;
  text-shadow: 3px 3px 4px black;
  font-size: 1.25em;
  margin: 0.5em;
  padding: 0 1em;

  .date-time {
    text-align: right;
  }
}
</style>

<style lang="scss">
.image-carousel {
  .info-container {
    .weather-container {
      margin-bottom: 0.5em;

      h1 {
        justify-content: left;
        margin-bottom: -0.5em;
        font-size: 0.8em;
      }
    }

    .date-time {
      .date {
        font-size: 2em;
      }

      .time {
        font-size: 4em;
      }
    }
  }
}
</style>
