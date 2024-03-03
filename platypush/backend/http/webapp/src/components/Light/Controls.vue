<template>
  <div class="controls light-controls" @click="$event.stopPropagation()">
    <Loading v-if="loading" />

    <div class="row" v-if="state.bri != null">
      <div class="col-1 icon">
        <i class="fas fa-sun" />
      </div>
      <div class="col-11 control">
        <Slider :range="colorConverter.ranges.bri" :disabled="loading" :value="state.bri"
                @change.stop="$emit(light ? 'set-light' : 'set-group', {brightness: parseInt($event.target.value)})" />
      </div>
    </div>

    <div class="row" v-if="state.ct != null">
      <div class="col-1 icon">
        <i class="fas fa-thermometer-half" />
      </div>
      <div class="col-11 control">
        <Slider :range="colorConverter.ranges.ct" :disabled="loading" :value="state.ct"
                @change.stop="$emit(light ? 'set-light' : 'set-group', {temperature: parseInt($event.target.value)})" />
      </div>
    </div>

    <label class="row" v-if="rgbColor">
      <span class="col-1 icon">
        <i class="fas fa-palette" />
      </span>
      <span class="col-11 control">
        <input type="color" :value="rgbColor" @change.stop="onColorSelect" />
      </span>
    </label>
  </div>
</template>

<script>
import Slider from "@/components/elements/Slider";
import Loading from "@/components/Loading";
import {ColorConverter} from "@/components/panels/Light/color";

export default {
  name: "Controls",
  components: {Loading, Slider},
  emits: ['set-light', 'set-group'],
  props: {
    light: {
      type: Object,
    },

    lights: {
      type: Object,
    },

    group: {
      type: Object,
    },

    loading: {
      type: Boolean,
      default: false,
    },

    colorConverter: {
      type: Object,
      default: () => new ColorConverter(),
    },
  },

  computed: {
    state() {
      if (this.light?.state)
        return this.light.state

      const state = this.group?.state || {}
      if (!this.lights)
        return state

      const avg = (values) => {
        if (!(values && values.length))
          return 0

        if (values[0] instanceof Array)
          return [...values[0].keys()].map((i) => {
            return avg(values.map((value) => value[i]))
          })

        return values.reduce((sum, value) => sum+value, 0) / values.length
      }

      return {
        ...state,
        ...Object.entries(
            Object.values(this.lights).reduce((obj, light) => {
              ['bri', 'hue', 'sat', 'rgb', 'xy', 'red', 'green', 'blue', 'ct'].forEach((attr) => {
                if (light.state?.[attr] != null) {
                  obj[attr] = [...(obj[attr] || []), light.state[attr]]
                }
              })

              return obj
            }, {})
        ).reduce((obj, [attr, values]) => {
          obj[attr] = avg(values)
          return obj
        }, {})
      }
    },

    color() {
      return this.getColor(this.state)
    },

    rgbColor() {
      const rgb = this.colorConverter.toRGB(this.state)
      if (rgb)
        return '#' + rgb.map((x) => {
          let hex = x.toString(16)
          if (hex.length < 2)
            hex = '0' + hex
          return hex
        }).join('')

      return null
    },
  },

  methods: {
    onColorSelect(event) {
      const rgb = event.target.value.slice(1).split(/(?=(?:..)*$)/).map((t) => parseInt(`0x${t}`))
      this.$emit(this.light ? 'set-light' : 'set-group', {
        rgb: rgb,
        xy: this.colorConverter.rgbToXY(...rgb),
        hsl: this.colorConverter.rgbToHsl(...rgb),
        brightness: this.colorConverter.rgbToBri(...rgb),
      })
    },

    getColor(state) {
      return {
        rgb: this.colorConverter.toRGB(state),
        xy: this.colorConverter.toXY(state),
        hsl: this.colorConverter.toHSL(state),
      }
    },
  },
}
</script>

<style lang="scss" scoped>
$light-controls-bg: white;

.controls {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 2.25em;
  background: $light-controls-bg;
  padding: 0.5em 1em;
  border-radius: 1em;
  box-shadow: $plugin-panel-shadow;

  .row {
    width: 100%;
    display: flex;
    align-items: center;
  }

  .control {
    padding-top: 0.25em;
  }

  .icon {
    opacity: 0.7;
  }

  input[type=color] {
    width: 100%;
    border: 0;
  }
}
</style>

<style lang="scss">
.light-controls {
  .row {
    .slider {
      margin-top: 0.4em;
    }
  }
}
</style>
