<template>
  <div class="controls animation-controls" @click="$event.stopPropagation()">
    <Loading v-if="loading" />

    <div class="animation-container">
      <div class="animation-header">
        <div class="row">
          <div class="col-3">
            Run Animation
          </div>
          <div class="col-9">
            <ToggleSwitch :value="animationRunning" @input="toggleAnimation" />
          </div>
        </div>

        <div class="row">
          <div class="col-3">Animation</div>
          <div class="col-9">
            <label>
              <select class="selector" @click="selectedAnimation = $event.target.value">
                <option value="color_transition">Color transition</option>
                <option value="blink">Blink</option>
              </select>
            </label>
          </div>
        </div>
      </div>

      <div class="animation">
        <div class="row" v-if="selectedAnimation === 'color_transition'">
          <div class="col-3">
            Hue range
          </div>
          <div class="col-9">
            <RangeSlider :range="colorConverter.ranges.hue" :disabled="loading"
                         :value="animations.color_transition.hue_range"
                         @mouseup="animations.color_transition.hue_range = $event.target.value" />
          </div>
        </div>

        <div class="row" v-if="selectedAnimation === 'color_transition'">
          <div class="col-3">
            Sat range
          </div>
          <div class="col-9">
            <RangeSlider :range="colorConverter.ranges.sat" :disabled="loading"
                         :value="animations.color_transition.sat_range"
                         @mouseup="animations.color_transition.sat_range = $event.target.value" />
          </div>
        </div>

        <div class="row" v-if="selectedAnimation === 'color_transition'">
          <div class="col-3">
            Bri range
          </div>
          <div class="col-9">
            <RangeSlider :range="colorConverter.ranges.sat" :disabled="loading"
                         :value="animations.color_transition.bri_range"
                         @mouseup="animations.color_transition.bri_range = $event.target.value" />
          </div>
        </div>

        <div class="row" v-if="selectedAnimation === 'color_transition'">
          <div class="col-3">
            Hue step
          </div>
          <div class="col-9">
            <Slider :range="colorConverter.ranges.hue" :disabled="loading"
                    :value="animations.color_transition.hue_step"
                    @mouseup="animations.color_transition.hue_step = parseFloat($event.target.value)" />
          </div>
        </div>

        <div class="row" v-if="selectedAnimation === 'color_transition'">
          <div class="col-3">
            Sat step
          </div>
          <div class="col-9">
            <Slider :range="colorConverter.ranges.sat" :disabled="loading"
                    :value="animations.color_transition.sat_step"
                    @mouseup="animations.color_transition.sat_step = parseFloat($event.target.value)" />
          </div>
        </div>

        <div class="row" v-if="selectedAnimation === 'color_transition'">
          <div class="col-3">
            Bri step
          </div>
          <div class="col-9">
            <Slider :range="colorConverter.ranges.bri" :disabled="loading"
                    :value="animations.color_transition.bri_step"
                    @mouseup="animations.color_transition.bri_step = parseFloat($event.target.value)" />
          </div>
        </div>

        <div class="row">
          <div class="col-3">
            Refresh seconds
          </div>
          <div class="col-9">
            <label>
              <input type="number" :value="animations[selectedAnimation].transition_seconds" step="0.1"
                     @input="animations[selectedAnimation].transition_seconds = parseFloat($event.target.value)" >
            </label>
          </div>
        </div>

        <div class="row">
          <div class="col-3">
            Duration (seconds)
          </div>
          <div class="col-9">
            <label>
              <input type="number" :value="animations[selectedAnimation].duration" step="5"
                     @input="animations[selectedAnimation].duration = $event.target.value?.length ? parseFloat($event.target.value) : null" >
            </label>
          </div>
        </div>
      </div>
    </div>

    <div class="lights">
      <div class="row">
        <label>
          <input type="checkbox"
                 :checked="Object.keys(lights).length === Object.values(selectedLights).filter((v) => v).length" @click="toggleSelectAll">
          Select all lights
        </label>
      </div>

      <div class="row" v-for="(light, id) in lights" :key="id">
        <label>
          <input type="checkbox" v-model="selectedLights[id]" @input="selectedLights[id] = !selectedLights[id]">
          {{ light.name }}
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import {ColorConverter} from "@/components/panels/Light/color";
import RangeSlider from "@/components/elements/RangeSlider";
import Slider from "@/components/elements/Slider";
import ToggleSwitch from "@/components/elements/ToggleSwitch";
import Utils from "@/Utils";

export default {
  name: "Animate",
  mixins: [Utils],
  components: {ToggleSwitch, Slider, RangeSlider, Loading},
  emits: ['start', 'stop'],
  props: {
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

    runningAnimations: {
      type: Object,
      default: () => {},
    }
  },

  data() {
    return {
      selectedAnimation: 'color_transition',
      animation: {},
      selectedLights: Object.keys(this.lights).reduce((obj, lightId) => {
        obj[lightId] = true
        return obj
      }, {}),
      animations: {
        color_transition: {
          hue_range: this.colorConverter.ranges.hue,
          sat_range: [
            parseInt((this.colorConverter.ranges.sat[1] - this.colorConverter.ranges.sat[0])/2),
            this.colorConverter.ranges.sat[1]
          ],
          bri_range: [
            parseInt((this.colorConverter.ranges.bri[1] - this.colorConverter.ranges.bri[0]) * 0.75),
            this.colorConverter.ranges.bri[1]
          ],

          hue_step: parseInt((this.colorConverter.ranges.hue[1] - this.colorConverter.ranges.hue[0]) / 25),
          sat_step: parseInt((this.colorConverter.ranges.sat[1] - this.colorConverter.ranges.sat[0]) / 50),
          bri_step: parseInt((this.colorConverter.ranges.bri[1] - this.colorConverter.ranges.bri[0]) / 50),
          transition_seconds: 1,
          duration: null,
        },

        blink: {
          transition_seconds: 1,
          duration: null,
        },
      },
    }
  },

  computed: {
    animationRunning() {
      return Object.keys(this.runningAnimations).length > 0
    },
  },

  methods: {
    toggleSelectAll() {
      const select = Object.values(this.selectedLights).filter((v) => v).length < Object.keys(this.lights).length
      Object.keys(this.lights).forEach((lightId) => {
        this.selectedLights[lightId] = select
      })
    },

    toggleAnimation() {
      const eventType = this.animationRunning ? 'stop' : 'start'
      const selectedLights = Object.entries(this.selectedLights).filter((light) => light[1]).map((light) => light[0])
      if (!selectedLights.length) {
        this.warn('No lights have been selected')
        return
      }

      this.$emit(eventType, {
        lights: selectedLights,
        animation: {
          ...this.animations[this.selectedAnimation],
          animation: this.selectedAnimation,
        },
      })
    },
  },
}
</script>

<style lang="scss" scoped>
$light-controls-bg: white;

.animation-container {
  width: 100%;

  .animation-header,
  .animation {
    padding-bottom: 0.5em;
    margin-bottom: 0.5em;
    box-shadow: $border-shadow-bottom;
  }
}

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

  .selector {
    width: 100%;
  }

  .row {
    width: 100%;
    display: flex;
    align-items: center;
    padding: 0.5em 0;

    & > div:last-child {
      text-align: right;
    }
  }

  .control {
    padding-top: 0.25em;
  }

  .lights {
    padding-top: 0.5em;
    width: 100%;

    .row {
      display: flex;
      align-items: center;
    }

    label {
      width: 100%;
    }
  }
}
</style>
